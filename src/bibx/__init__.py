import dataclasses
from typing import TextIO

import networkx as nx

from bibx.entities.article import Article
from bibx.entities.collection import Collection
from bibx.entities.collection_builders.isi import IsiCollectionBuilder
from bibx.entities.collection_builders.scopus import ScopusCollectionBuilder


def read_scopus(*files: TextIO) -> Collection:
    """
    Takes any number of bibtex files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusCollectionBuilder(*files).build()


def read_wos(*files: TextIO) -> Collection:
    """
    Takes any number of wos text files and returns a collection.

    :param files: WoS files open.
    :return: the collection
    """
    return IsiCollectionBuilder(*files).build()


def _add_article_info(g: nx.DiGraph, article: Article):
    for key, val in dataclasses.asdict(article).items():
        if key in ("sources", "references") or key.startswith("_"):
            continue
        try:
            g.nodes[article.key][key] = val
        except KeyError:
            g.add_node(article.key, **{key: val})


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


def clean_graph(g: nx.DiGraph) -> nx.DiGraph:
    """
    Clean a graph to make it ready for the sap algorithm.

    :param g: graph with unnecessary nodes
    :return: cleaned up giant component
    """
    # Extract the giant component of the graph
    giant_component_nodes = max(nx.weakly_connected_components(g), key=len)
    giant_component: nx.DiGraph = g.subgraph(giant_component_nodes).copy()

    # Remove nodes that cite one element and are never cited themselves
    giant_component.remove_nodes_from(
        [
            n
            for n in giant_component
            if giant_component.in_degree(n) == 1  # noqa
            and giant_component.out_degree(n) == 0  # noqa
        ]
    )

    # Break loops
    loops = [
        loop
        for loop in nx.strongly_connected_components(giant_component)
        if len(loop) > 1
    ]
    for loop in loops:
        giant_component.remove_edges_from([(u, v) for u in loop for v in loop])

    return giant_component
