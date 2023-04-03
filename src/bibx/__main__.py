import networkx as nx

from bibx import clean_graph, create_graph, read_scopus
from bibx.algorithms.sap import Sap


def create_toy_graph() -> nx.DiGraph:
    #      a
    #      |
    #      b
    #    / | \
    #   c  d  e
    graph = nx.DiGraph()
    for node in "abcde":
        graph.add_node(node, year=2000)
    graph.add_edge("a", "b")
    for node in "cde":
        graph.add_edge("b", node)
    return graph


def create_real_graph() -> nx.DiGraph:
    with open("./docs/examples/scopus.bib") as f:
        c = read_scopus(f)
    graph = create_graph(c)
    graph = clean_graph(graph)
    return graph


if __name__ == "__main__":
    # graph = create_toy_graph()
    graph = create_real_graph()
    s = Sap()
    graph = s.tree(graph)
    print(graph)
