import networkx as nx

from bibx.algorithms.sap import Sap


def create_toy_graph() -> nx.DiGraph:
    r"""
    Creates a toy graph with known sap.

    The toy graph has the following shape:

    a   b   c
      \ | /
        d
      / | \
    e   f   g
    """

    g = nx.DiGraph()
    for n in "abcdefg":
        # we need to have years for all the nodes
        g.add_node(n, year=2000)
    for n in "abc":
        g.add_edge(n, "d")
    for n in "efg":
        g.add_edge("d", n)
    return g


def test_sap():
    g = create_toy_graph()
    s = Sap()
    g = s.tree(g)

    # a, b and c should be leaves
    for n in "abc":
        assert g.nodes[n]["leaf"] > 0
        assert g.nodes[n]["trunk"] == 0
        assert g.nodes[n]["root"] == 0

    # e, f, and g should be roots
    for n in "efg":
        assert g.nodes[n]["leaf"] == 0
        assert g.nodes[n]["trunk"] == 0
        assert g.nodes[n]["root"] > 0

    # node d should be the trunk
    assert g.nodes["d"]["leaf"] == 0
    assert g.nodes["d"]["trunk"] > 0
    assert g.nodes["d"]["root"] == 0
