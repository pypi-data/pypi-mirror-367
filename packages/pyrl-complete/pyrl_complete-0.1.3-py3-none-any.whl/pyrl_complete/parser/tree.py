# Copyright (C) 2025 codimoc, codimoc@prismoid.uk

from typing import List, Self, Optional, Dict
from .rules import Paths
from ..common.string_utils import find_all_char_positions, remove_first_word
import re


class Node:
    "A node in the parse tree"

    def __init__(self, name: str, parent: Optional[Self]):
        self.children: Dict[str, Node] = {}  # name -> node map for children
        self.name = name
        self.parent = parent

    def level(self) -> int:
        "Returns the level of the node in the tree"
        level = 0
        node = self
        while node.parent is not None:
            level += 1
            node = node.parent
        return level

    def expression(self) -> str:
        "Returns the expression to be matched against the input"
        if self.name == "root":
            return ""
        if self.parent.name == "root":
            return self.name
        return f"{self.parent.expression()} {self.name}"

    def matches(self, input: str) -> bool:
        exp = self.expression()
        if "?" not in exp:
            return exp.startswith(input.lower())
        # remove double spaces from input
        input = re.sub(r"\s+", " ", input)
        # find position of '?' in exp
        placeholders = find_all_char_positions(exp, "?")
        if len(placeholders) == 0:
            return False

        while len(placeholders) > 0:
            p = placeholders[0]
            input = remove_first_word(input, p)
            exp = exp[:p] + exp[p + 1:]
            placeholders = find_all_char_positions(exp, "?")

        # remove double spaces from exp
        exp = re.sub(r"\s+", " ", exp)
        input = re.sub(r"\s+", " ", input)      
        return exp.startswith(input.lower())
    

class Tree:
    "The full parse tree represntation of the grammar"

    def __init__(self, paths: Paths):
        self.root: Node = Node("root", None)
        self.cache: Dict[str, List[Node]] = (
            {}
        )  # a map from partial string input to Node list
        self._populate_tree_from_paths(paths)

    def _populate_path(self, start_node: Node, path_segments: List[str]):
        """
        Populates a single path into the tree starting from start_node.
        """
        current_node = start_node
        for segment in path_segments:
            if segment not in current_node.children:
                current_node.children[segment] = Node(segment, current_node)
            current_node = current_node.children[segment]

    def _populate_tree_from_paths(self, paths_list: Paths):
        "Populate the entire tree from the list of paths"
        for p in paths_list:
            self._populate_path(self.root, p)

    def find_matching_nodes(self, input: str, root: Node = None) -> List[Node]:
        "Find a list of nodes matching the input"
        if root is None:
            root = self.root
        # only use the cache at the root of the tree
        if root.level() == 0 and input in self.cache:
            return self.cache[input]
        nodes = []
        if root.matches(input):
            nodes.append(root)
        for n in root.children.values():
            nodes.extend(self.find_matching_nodes(input, n))
        # only at root level
        if root.level() == 0:
            self.cache[input] = nodes
        return nodes

    def get_suggestions(self, input: str, root: Node = None) -> List[str]:
        "Returns a list of suggestions based on the input"
        if root is None:
            root = self.root
        nodes = self.find_matching_nodes(input, root)
        return [n.expression() for n in nodes]

    def get_predictions(self, input: str, root: Node = None) -> List[str]:
        "Returns a list of predictions based on the input"
        if root is None:
            root = self.root
        nodes = self.find_matching_nodes(input, root)
        nodes = [n for n in nodes if n.name != "root"]
        min_level = 10000
        for n in nodes:
            if n.level() < min_level:
                min_level = n.level()
        nodes = [n for n in nodes if n.level() == min_level]
        return [n.expression() for n in nodes]
