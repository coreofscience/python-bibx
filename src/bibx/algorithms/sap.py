import dataclasses
import logging
from typing import Any, List, Set, Tuple, cast

import networkx as nx
from networkx.algorithms.community.louvain import louvain_communities

from bibx import Article, Collection

YEAR = "year"
LEAF = "leaf"
ROOT = "root"
TRUNK = "trunk"
BRANCH = "branch"
SAP = "_sap"
LEAF_CONNECTIONS = "_leaf_connections"
ELABORATE_SAP = "_elaborate_sap"
ROOT_CONNECTIONS = "_root_connections"
RAW_SAP = "_raw_sap"

logger = logging.getLogger(__name__)


def _limit(attribute: List[Tuple[Any, int]], _max: int):
    if _max is not None:
        sorted_attribute = sorted(attribute, key=lambda x: x[1], reverse=True)
        attribute = sorted_attribute[:_max]
    return attribute


def _add_article_info(g: nx.DiGraph, article: Article):
    for key, val in dataclasses.asdict(article).items():
        if key in ("sources", "references") or key.startswith("_"):
            continue
        try:
            g.nodes[article.key][key] = val
        except KeyError:
            g.add_node(article.key, **{key: val})


class Sap:
    def __init__(
        self,
        max_roots: int = 20,
        max_leaves: int = 50,
        max_trunk: int = 20,
        min_leaf_connections: int = 3,
        max_leaf_age: int = 7,
        max_branch_size: int = 15,
    ):
        """
        Create a Sap instance with the given parameters.

        :param max_roots: maximum number of roots on the tree
        :param max_leaves: maximum number of leaves on the tree
        :param max_trunk: maximum number of trunk nodes in the tree
        :param min_leaf_connections: minimum number of connections between leaves and roots
        :param max_leaf_age: maximum age for a leaf
        """
        self.max_roots = max_roots
        self.max_leaves = max_leaves
        self.max_trunk = max_trunk
        self.min_leaf_connections = min_leaf_connections
        self.max_leaf_age = max_leaf_age
        self.max_branch_size = max_branch_size

    @staticmethod
    def create_graph(collection: Collection) -> nx.DiGraph:
        """
        Creates a `networkx.DiGraph` from a `Collection`.

        It uses the article label as a key and adds all the properties of the article to
        the graph.

        :param collection: a `bibx.Collection` instance.
        :return: a `networkx.DiGraph` instance.
        """
        g = nx.DiGraph()
        g.add_edges_from((u.key, v.key) for u, v in collection.citation_pairs)
        for article in collection.articles:
            for reference in article.references:
                _add_article_info(g, reference)
        for article in collection.articles:
            _add_article_info(g, article)
        g.remove_edges_from(nx.selfloop_edges(g))
        return g

    @staticmethod
    def clean_graph(g: nx.DiGraph) -> nx.DiGraph:
        """
        Clean a graph to make it ready for the sap algorithm.

        :param g: graph with unnecessary nodes
        :return: cleaned up giant component
        """
        # Extract the giant component of the graph
        giant_component_nodes = max(nx.weakly_connected_components(g), key=len)
        giant: nx.DiGraph = g.subgraph(giant_component_nodes).copy()

        # Remove nodes that cite one element and are never cited themselves
        giant.remove_nodes_from(
            [
                n
                for n in giant
                if giant.in_degree(n) == 1 and giant.out_degree(n) == 0  # noqa  # noqa
            ]
        )

        # Break loops
        loops = [
            loop for loop in nx.strongly_connected_components(giant) if len(loop) > 1
        ]
        for loop in loops:
            giant.remove_edges_from([(u, v) for u in loop for v in loop])

        return giant

    def tree(self, graph: nx.DiGraph, clear: bool = False) -> nx.DiGraph:
        """
        Computes the whole tree.
        """
        graph = cast(nx.DiGraph, graph.copy())
        graph = self._compute_root(graph)
        graph = self._compute_leaves(graph)
        graph = self._compute_sap(graph)
        graph = self._compute_trunk(graph)
        graph = self._compute_branches(graph)
        if clear:
            graph = self._clear(graph)
        return graph

    def _compute_root(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Takes in a connected graph and returns it labeled with a `root` property.
        :return: Labeled graph with the root property.
        """
        g = cast(nx.DiGraph, graph.copy())
        valid_roots = [
            (n, cast(int, g.in_degree(n)))
            for n in g.nodes
            if g.out_degree(n) == 0  # noqa
        ]
        sorted_roots = _limit(valid_roots, self.max_roots)
        nx.set_node_attributes(g, 0, ROOT)
        for node, degree in sorted_roots:
            g.nodes[node][ROOT] = degree
        return g

    def _compute_leaves(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Takes in a connected graph and returns it labeled with a `leaf` property.
        :param graph: Connected and filtered graph to work with.
        :return: Labeled graph with the leaf property.
        """
        g = cast(nx.DiGraph, graph.copy())
        try:
            roots = [n for n, d in g.nodes.items() if d[ROOT] > 0]
        except AttributeError:
            raise TypeError("It's necessary to have some roots")
        if not roots:
            raise TypeError("It's necessary to have some roots")

        nx.set_node_attributes(g, 0, ROOT_CONNECTIONS)
        for node in roots:
            g.nodes[node][ROOT_CONNECTIONS] = 1
        topological_order = list(nx.topological_sort(g))
        for node in reversed(topological_order):
            nbs = list(g.successors(node))
            if nbs:
                g.nodes[node][ROOT_CONNECTIONS] = sum(
                    g.nodes[n][ROOT_CONNECTIONS] for n in nbs
                )

        potential_leaves = [
            (node, g.nodes[node][ROOT_CONNECTIONS])
            for node in g.nodes
            if g.in_degree(node) == 0  # noqa
        ]
        extended_leaves = potential_leaves[:]

        if self.min_leaf_connections is not None:
            potential_leaves = [
                (n, c) for n, c in potential_leaves if c >= self.min_leaf_connections
            ]

        if self.max_leaf_age is not None:
            potential_leaves = [
                (n, c) for n, c in potential_leaves if YEAR in g.nodes[n]
            ]
            newest_year = max(
                g.nodes[n][YEAR] for n, _ in potential_leaves if g.nodes[n][YEAR]
            )
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

    @staticmethod
    def _compute_sap(graph: nx.DiGraph) -> nx.DiGraph:
        """
        Computes the sap of each node.
        """
        g = cast(nx.DiGraph, graph.copy())
        try:
            valid_root = [n for n, d in g.nodes.items() if d[ROOT] > 0]
            valid_leaves = [n for n, d in g.nodes.items() if d[LEAF] > 0]
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

    def _compute_trunk(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Tags leaves.
        """
        g = cast(nx.DiGraph, graph.copy())
        try:
            potential_trunk = [
                (n, d[SAP])
                for n, d in g.nodes.items()
                if d[ROOT] == 0 and d[LEAF] == 0 and d[SAP] > 0
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

    def _compute_branches(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Tags branches.
        """
        g = cast(nx.DiGraph, graph.copy())
        undirected = g.to_undirected()
        communities: List[Set] = louvain_communities(undirected)
        branches = list(sorted(communities, key=len))[:3]
        nx.set_node_attributes(g, 0, BRANCH)
        for i, branch in enumerate(branches, start=1):
            potential_branch = [
                (n, g.nodes[n][YEAR])
                for n in branch
                if g.nodes[n][ROOT] == 0 and g.nodes[n][TRUNK] == 0
            ]
            potential_branch = _limit(potential_branch, self.max_branch_size)
            for node, _ in potential_branch:
                g.nodes[node][BRANCH] = i
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
