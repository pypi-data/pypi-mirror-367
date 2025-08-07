import html
import json
import logging
import numbers
import os
import re
from datetime import datetime
from hashlib import md5
from typing import Any, Union, List

import networkx as nx
from networkx.readwrite import json_graph

from duowen_agent.llm import tokenizer


def create_file_dir(file_name):
    dir_name = os.path.dirname(file_name)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)


def compute_args_hash(*args):
    return md5(str(args).encode()).hexdigest()


def print_call_back(msg: str):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {msg}")


def is_interrupt():
    """集成系统需要实现的中断函数"""
    return False


def clean_str(input: Any) -> str:
    """Clean an input string by removing HTML escapes, control characters, and other unwanted characters."""
    # If we get non-string input, just give it back
    if not isinstance(input, str):
        return input

    result = html.unescape(input.strip())
    # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
    return re.sub(r"[\"\x00-\x1f\x7f-\x9f]", "", result)


def is_float_regex(value):
    return bool(re.match(r"^[-+]?[0-9]*\.?[0-9]+$", value))


def flat_uniq_list(arr, key):
    res = []
    for a in arr:
        a = a[key]
        if isinstance(a, list):
            res.extend(a)
        else:
            res.append(a)
    return list(set(res))


def truncate(string: str, max_len: int) -> str:
    return tokenizer.truncate_emb(string, max_len)


def tidy_graph(graph: nx.Graph, callback, check_attribute: bool = True):
    """
    Ensure all nodes and edges in the graph have some essential attribute.
    """

    def is_valid_item(node_attrs: dict) -> bool:
        valid_node = True
        for attr in ["description", "source_id"]:
            if attr not in node_attrs:
                valid_node = False
                break
        return valid_node

    if check_attribute:
        purged_nodes = []
        for node, node_attrs in graph.nodes(data=True):
            if not is_valid_item(node_attrs):
                purged_nodes.append(node)
        for node in purged_nodes:
            graph.remove_node(node)
        if purged_nodes and callback:
            callback(f"由于缺少基本属性，从图中清除 {len(purged_nodes)} 节点")

    purged_edges = []
    for source, target, attr in graph.edges(data=True):
        if check_attribute:
            if not is_valid_item(attr):
                purged_edges.append((source, target))

    for source, target in purged_edges:
        graph.remove_edge(source, target)
    if purged_edges and callback:
        callback(f"由于缺少基本属性，从图中清除 {len(purged_edges)} 边。")


def dump_graph(graph: nx.Graph):
    return json.dumps(
        nx.node_link_data(graph, edges="edges"), ensure_ascii=False, indent=2
    )


def load_json_graph(content):
    return json_graph.node_link_graph(json.loads(content), edges="edges")


def get_from_to(node1, node2):
    if node1 < node2:
        return node1, node2
    else:
        return node2, node1


def dict_has_keys_with_types(
    data: dict, expected_fields: list[tuple[str, type]]
) -> bool:
    """Return True if the given dictionary has the given keys with the given types."""
    for field, field_type in expected_fields:
        if field not in data:
            return False

        value = data[field]
        if not isinstance(value, field_type):
            return False
    return True


def parse_value(value: str):
    """Convert a string value to its appropriate type (int, float, bool, None, or keep as string). Work as a more broad 'eval()'"""
    value = value.strip()

    if value == "null":
        return None
    elif value == "true":
        return True
    elif value == "false":
        return False
    else:
        # Try to convert to int or float
        try:
            if "." in value:  # If there's a dot, it might be a float
                return float(value)
            else:
                return int(value)
        except ValueError:
            # If conversion fails, return the value as-is (likely a string)
            return value.strip('"')  # Remove surrounding quotes if they exist


def extract_first_complete_json(s: str):
    """Extract the first complete JSON object from the string using a stack to track braces."""
    stack = []
    first_json_start = None

    for i, char in enumerate(s):
        if char == "{":
            stack.append(i)
            if first_json_start is None:
                first_json_start = i
        elif char == "}":
            if stack:
                start = stack.pop()
                if not stack:
                    first_json_str = s[first_json_start : i + 1]
                    try:
                        # Attempt to parse the JSON string
                        return json.loads(first_json_str.replace("\n", ""))
                    except json.JSONDecodeError as e:
                        logging.error(
                            f"JSON decoding failed: {e}. Attempted string: {first_json_str[:50]}..."
                        )
                        return None
                    finally:
                        first_json_start = None
    logging.warning("No complete JSON object found in the input string.")
    return None


def extract_values_from_json(json_string):
    """Extract key values from a non-standard or malformed JSON string, handling nested objects."""
    extracted_values = {}

    # Enhanced pattern to match both quoted and unquoted values, as well as nested objects
    regex_pattern = r'(?P<key>"?\w+"?)\s*:\s*(?P<value>{[^}]*}|".*?"|[^,}]+)'

    for match in re.finditer(regex_pattern, json_string, re.DOTALL):
        key = match.group("key").strip('"')  # Strip quotes from key
        value = match.group("value").strip()

        # If the value is another nested JSON (starts with '{' and ends with '}'), recursively parse it
        if value.startswith("{") and value.endswith("}"):
            extracted_values[key] = extract_values_from_json(value)
        else:
            # Parse the value into the appropriate type (int, float, bool, etc.)
            extracted_values[key] = parse_value(value)

    if not extracted_values:
        logging.warning("No values could be extracted from the string.")

    return extracted_values


def convert_response_to_json(response: str) -> dict:
    """Convert response string to JSON, with error handling and fallback to non-standard JSON extraction."""
    prediction_json = extract_first_complete_json(response)

    if prediction_json is None:
        logging.info("Attempting to extract values from a non-standard JSON string...")
        prediction_json = extract_values_from_json(response)

    if not prediction_json:
        logging.error("Unable to extract meaningful data from the response.")
    else:
        logging.info("JSON data successfully extracted.")

    return prediction_json


def truncate_list_by_token_size(
    list_data: list,
    key: callable,
    max_token_size: int,
):
    """Truncate a list of data by token size using a provided tokenizer wrapper."""
    if max_token_size <= 0:
        return []
    tokens = 0
    for i, data in enumerate(list_data):
        tokens += (
            len(tokenizer.chat_encode(key(data))) + 1
        )  # 防御性，模拟通过\n拼接列表的情况
        if tokens > max_token_size:
            return list_data[:i]
    return list_data


def enclose_string_with_quotes(content: Any) -> str:
    """Enclose a string with quotes"""
    if isinstance(content, numbers.Number):
        return str(content)
    content = str(content)
    content = content.strip().strip("'").strip('"')
    return f'"{content}"'


def list_of_list_to_csv(data: list[list]):
    return "\n".join(
        [
            ",\t".join([f"{enclose_string_with_quotes(data_dd)}" for data_dd in data_d])
            for data_d in data
        ]
    )


def split_string_by_multi_markers(content: str, markers: list[str]) -> list[str]:
    """Split a string by multiple markers"""
    if not markers:
        return [content]
    results = re.split("|".join(re.escape(marker) for marker in markers), content)
    return [r.strip() for r in results if r.strip()]


class NetworkXUtils:

    def __init__(self, graph: nx.Graph | str = None):
        if isinstance(graph, str):
            self._graph = self.loads(graph)
        elif isinstance(graph, nx.Graph):
            self._graph = graph
        elif graph is None:
            self._graph = nx.Graph()
        else:
            raise ValueError("graph must be a nx.Graph instance or a json string")

    def has_node(self, node_id: str) -> bool:
        return self._graph.has_node(node_id)

    def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
        return self._graph.has_edge(source_node_id, target_node_id)

    def get_node(self, node_id: str) -> Union[dict, None]:
        return self._graph.nodes.get(node_id)

    def number_of_nodes(self) -> int:
        return self._graph.number_of_nodes()

    def number_of_edges(self) -> int:
        return self._graph.number_of_edges()

    def graph_density(self) -> float:
        return nx.density(self._graph)

    def get_nodes_batch(self, node_ids: list[str]) -> list[Union[dict, None]]:
        return [self.get_node(node_id) for node_id in node_ids]

    def node_degree(self, node_id: str) -> int:
        # [numberchiffre]: node_id not part of graph returns `DegreeView({})` instead of 0
        return self._graph.degree(node_id) if self._graph.has_node(node_id) else 0

    def node_degrees_batch(self, node_ids: List[str]) -> List[int]:
        return [self.node_degree(node_id) for node_id in node_ids]

    def edge_degree(self, src_id: str, tgt_id: str) -> int:
        return (self._graph.degree(src_id) if self._graph.has_node(src_id) else 0) + (
            self._graph.degree(tgt_id) if self._graph.has_node(tgt_id) else 0
        )

    def edge_degrees_batch(self, edge_pairs: list[tuple[str, str]]) -> list[int]:
        return [self.edge_degree(src_id, tgt_id) for src_id, tgt_id in edge_pairs]

    def get_edge(self, source_node_id: str, target_node_id: str) -> Union[dict, None]:
        return self._graph.edges.get((source_node_id, target_node_id))

    def get_edges_batch(
        self, edge_pairs: list[tuple[str, str]]
    ) -> list[Union[dict, None]]:
        return [
            self.get_edge(source_node_id, target_node_id)
            for source_node_id, target_node_id in edge_pairs
        ]

    def get_node_edges(self, source_node_id: str):
        if self._graph.has_node(source_node_id):
            return list(self._graph.edges(source_node_id))
        return None

    def get_nodes_edges_batch(self, node_ids: list[str]) -> list[list[tuple[str, str]]]:
        return [self.get_node_edges(node_id) for node_id in node_ids]

    def upsert_node(self, node_id: str, node_data: dict[str, str]):
        self._graph.add_node(node_id, **node_data)

    def upsert_nodes_batch(self, nodes_data: list[tuple[str, dict[str, str]]]):
        for node_id, node_data in nodes_data:
            self.upsert_node(node_id, node_data)

    def upsert_edge(
        self, source_node_id: str, target_node_id: str, edge_data: dict[str, str]
    ):
        self._graph.add_edge(source_node_id, target_node_id, **edge_data)

    def upsert_edges_batch(self, edges_data: list[tuple[str, str, dict[str, str]]]):
        for source_node_id, target_node_id, edge_data in edges_data:
            self.upsert_edge(source_node_id, target_node_id, edge_data)

    def pagerank(self):
        pr = nx.pagerank(self._graph)
        for node_name, pagerank in pr.items():
            self._graph.nodes[node_name]["pagerank"] = pagerank
        return self._graph

    def dumps(self):
        return dump_graph(self._graph)

    @staticmethod
    def loads(content: str):
        return json_graph.node_link_graph(json.loads(content), edges="edges")


def similarity_node(
    nodes: list[str],
    embeddings: list[list[float]],
    sim_threshold=0.75,
    min_cluster_size=2,
    max_cluster_size=100,
) -> List[list[str]]:
    from sklearn.metrics.pairwise import cosine_similarity

    sim_matrix = cosine_similarity(embeddings)

    G = nx.Graph()
    for i in range(len(nodes)):
        G.add_node(i, text=nodes[i])
        for j in range(i + 1, len(nodes)):
            if sim_matrix[i][j] > sim_threshold:
                G.add_edge(i, j)

    clusters = list(nx.connected_components(G))
    return [
        [nodes[i] for i in list(i)]
        for i in clusters
        if max_cluster_size >= len(i) >= min_cluster_size
    ]
