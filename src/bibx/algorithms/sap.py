import logging
from typing import List, Tuple

import networkx as nx

YEAR = "year"

CONNECTIONS = "_connections"

LEAF = "leaf"
ROOT = "root"
TRUNK = "trunk"
SAP = "_sap"
LEAF_CONNECTIONS = "_leaf_connections"
ELABORATE_SAP = "_elaborate_sap"
ROOT_CONNECTIONS = "_root_connections"
RAW_SAP = "_raw_sap"

logger = logging.getLogger(__name__)


def _limit(attribute: List[Tuple[str, int]], _max: int):
    if _max is not None:
        sorted_attribute = sorted(attribute, key=lambda x: x[1], reverse=True)
        attribute = sorted_attribute[:_max]
    return attribute


class Sap:
    def __init__(
        self,
        max_roots: int = 20,
        max_leaves: int = 50,
        max_trunk: int = 20,
        min_leaf_connections: int = 3,
        max_leaf_age: int = 7,
    ):
        self.max_roots = max_roots
        self.max_leaves = max_leaves
        self.max_trunk = max_trunk
        self.min_leaf_connections = min_leaf_connections
        self.max_leaf_age = max_leaf_age

    @staticmethod
    def _compute_sap(graph: nx.DiGraph) -> nx.DiGraph:
        """
        Computes the sap of each node.
        """
        g = graph.copy()
        try:
            valid_root = [n for n, d in g.nodes(data=True) if d[ROOT] > 0]
            valid_leaves = [n for n, d in g.nodes(data=True) if d[LEAF] > 0]
        except AttributeError:
            raise TypeError("The graph needs to have a 'root' and a 'leaf' attribute")
        if not valid_root or not valid_leaves:
            raise TypeError("The graph needs to have at least some roots and leafs")

        nx.set_node_attributes(g, 0, RAW_SAP)
        nx.set_node_attributes(g, 0, ROOT_CONNECTIONS)
        for node in valid_root:
            g.nodes[node][RAW_SAP] = g.nodes[node][ROOT]
            g.nodes[node][ROOT_CONNECTIONS] = 1
        for node in reversed(list(nx.topological_sort(g))):
            neighbors = list(g.successors(node))
            if neighbors:
                for attr in (RAW_SAP, ROOT_CONNECTIONS):
                    g.nodes[node][attr] = sum(g.nodes[nb][attr] for nb in neighbors)

        nx.set_node_attributes(g, 0, ELABORATE_SAP)
        nx.set_node_attributes(g, 0, LEAF_CONNECTIONS)
        for node in valid_leaves:
            g.nodes[node][ELABORATE_SAP] = g.nodes[node][LEAF]
            g.nodes[node][LEAF_CONNECTIONS] = 1
        for node in nx.topological_sort(g):
            neighbors = list(g.predecessors(node))
            if neighbors:
                for attr in (ELABORATE_SAP, LEAF_CONNECTIONS):
                    g.nodes[node][attr] = sum(g.nodes[nb][attr] for nb in neighbors)

        nx.set_node_attributes(g, 0, SAP)
        for node in g.nodes:
            g.nodes[node][SAP] = (
                g.nodes[node][LEAF_CONNECTIONS] * g.nodes[node][RAW_SAP]
                + g.nodes[node][ROOT_CONNECTIONS] * g.nodes[node][ELABORATE_SAP]
            )

        return g

    def _compute_root(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Takes in a connected graph and returns it labeled with a `root` property.
        :return: Labeled graph with the root property.
        """
        g = graph.copy()
        valid_roots = [
            (n, g.in_degree(n)) for n in g.nodes if g.out_degree(n) == 0
        ]  # noqa
        sorted_roots = _limit(valid_roots, self.max_trunk)
        nx.set_node_attributes(g, 0, ROOT)
        for (node, degree) in sorted_roots[: self.max_roots]:
            g.nodes[node][ROOT] = degree
        return g

    def _compute_leaves(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Takes in a connected graph and returns it labeled with a `leaf` property.
        :param graph: Connected and filtered graph to work with.
        :return: Labeled graph with the leaf property.
        """
        g = graph.copy()
        try:
            valid_root = [n for n, d in g.nodes(data=True) if d[ROOT] > 0]
        except AttributeError:
            raise TypeError("It's necessary to have some roots")
        if not valid_root:
            raise TypeError("It's necessary to have some roots")

        nx.set_node_attributes(g, 0, CONNECTIONS)
        for node in valid_root:
            g.nodes[node][CONNECTIONS] = 1
        topological_order = list(nx.topological_sort(g))
        for node in reversed(topological_order):
            nbs = list(g.successors(node))
            if nbs:
                g.nodes[node][CONNECTIONS] = sum(
                    g.nodes[n][CONNECTIONS] for n in nbs
                )

        potential_leaves = [
            (node, g.nodes[node][CONNECTIONS])
            for node in g.nodes
            if g.in_degree(node) == 0
        ]  # noqa
        extended_leaves = potential_leaves[:]

        if self.min_leaf_connections is not None:
            potential_leaves = [
                (n, c) for n, c in potential_leaves if c >= self.min_leaf_connections
            ]

        if self.max_leaf_age is not None:
            potential_leaves = [(n, c) for n, c in potential_leaves if YEAR in g.nodes[n]]
            newest_year = max(g.nodes[n][YEAR] for n, _ in potential_leaves if g.nodes[n][YEAR])
            earliest_publication_year = newest_year - self.max_leaf_age
            potential_leaves = [
                (n, c)
                for n, c in potential_leaves
                if g.nodes[n][YEAR] >= earliest_publication_year
            ]

        if not potential_leaves:
            logger.info(
                "Reverting leaf cut policies, as they remove all possible leaves"
            )
            potential_leaves = extended_leaves

        potential_leaves = _limit(potential_leaves, self.max_leaves)
        nx.set_node_attributes(g, 0, LEAF)
        for node, c in potential_leaves:
            g.nodes[node][LEAF] = c
        return g

    def _compute_trunk(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Tags leaves.
        """
        g = graph.copy()
        try:
            potential_trunk = [
                (n, g.nodes[n][SAP])
                for n in g.nodes
                if g.nodes[n][ROOT] == 0
                and g.nodes[n][LEAF] == 0
                and g.nodes[n][SAP] > 0
            ]
        except AttributeError:
            raise TypeError(
                "The graph needs to have a 'root', 'leaf' and 'sap' attributes"
            )
        if not potential_trunk:
            raise TypeError("The graph needs to have at least some nodes with sap")

        potential_trunk = _limit(potential_trunk, self.max_trunk)
        nx.set_node_attributes(g, 0, TRUNK)
        for node, sap in potential_trunk:
            g.nodes[node][TRUNK] = sap
        return g

    @staticmethod
    def _clear(graph: nx.DiGraph) -> nx.DiGraph:
        """
        Returns a copy of the graph clear of untagged nodes.
        """
        nodes = [
            n
            for n in graph.nodes
            if graph.nodes[n][ROOT] > 0
            and graph.nodes[n][TRUNK] > 0
            and graph.nodes[n][LEAF] > 0
        ]
        return graph.subgraph(nodes)

    def tree(self, graph: nx.DiGraph, clear: bool = False) -> nx.DiGraph:
        """
        Computes the whole tree.
        """
        graph = graph.copy()
        graph = self._compute_root(graph)
        graph = self._compute_leaves(graph)
        graph = self._compute_sap(graph)
        graph = self._compute_trunk(graph)
        if clear:
            graph = self._clear(graph)
        return graph