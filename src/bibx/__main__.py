from bibx import clean_graph, create_graph, read_scopus
from bibx.algorithms.sap import Sap

if __name__ == "__main__":

    with open("./docs/examples/scopus.bib") as f:
        c = read_scopus(f)

    g = create_graph(c)
    g = clean_graph(g)
    s = Sap()
    g = s.tree(g)

    print(g)
