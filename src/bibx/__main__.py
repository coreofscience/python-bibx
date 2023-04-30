import networkx as nx

from bibx import read_scopus_bib, read_wos
from bibx.algorithms.sap import Sap


def create_toy_graph() -> nx.DiGraph:
    #      a
    #      |
    #      b
    #    / | \
    #   c  d  e
    g = nx.DiGraph()
    for node in "abcde":
        g.add_node(node, year=2000)
    g.add_edge("a", "b")
    for node in "cde":
        g.add_edge("b", node)
    return g


def create_real_graph() -> nx.DiGraph:
    with open("./docs/examples/bit-pattern-savedrecs.txt") as f:
        isi_collection = read_wos(f)
    with open("./docs/examples/scopus.bib") as f:
        scopus_collection = read_scopus_bib(f)
    merged_collection = scopus_collection.merge(isi_collection)
    g = Sap.create_graph(merged_collection)
    g = Sap.clean_graph(g)
    return g


if __name__ == "__main__":
    # graph = create_toy_graph()
    graph = create_real_graph()
    s = Sap()
    graph = s.tree(graph)
    print(graph)
