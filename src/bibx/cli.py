from collections.abc import Callable
from enum import Enum
from typing import List, TextIO

import networkx as nx
import typer
from rich import print

from bibx import Collection, read_any, read_scopus_bib, read_scopus_ris, read_wos
from bibx.algorithms.preprocess import Preprocess
from bibx.algorithms.sap import Sap

app = typer.Typer()


class Format(Enum):
    WOS = "wos"
    RIS = "ris"
    BIB = "bib"


@app.command()
def describe(format: Format, filename: str):
    """
    Parses a file and provides a short description.
    """
    if format == Format.WOS:
        c = read_wos(open(filename))
        print(":boom: the file satisfies the ISI WOS format")
        print(f"There are {len(c.articles)} records parsed")
    if format == Format.RIS:
        c = read_scopus_ris(open(filename))
        print(":boom: the file satisfies the ISI WOS format")
        print(f"There are {len(c.articles)} records parsed")
    if format == Format.BIB:
        c = read_scopus_bib(open(filename))
        print(":boom: the file satisfies the ISI WOS format")
        print(f"There are {len(c.articles)} records parsed")


@app.command()
def toy_sap():
    """
    Runs the sap algorithm on a toy graph.
    """
    graph = nx.DiGraph()
    for node in "abcde":
        graph.add_node(node, year=2000)
    graph.add_edge("a", "b")
    for node in "cde":
        graph.add_edge("b", node)
    s = Sap()
    graph = s.tree(graph)
    print(graph)


@app.command()
def sap(filename: str):
    """
    Runs the sap algorithm on a seed file of any supported format.
    """
    with open(filename) as f:
        collection = read_any(f)

    s = Sap()
    graph = s.create_graph(collection)
    graph = s.clean_graph(graph)
    graph = s.tree(graph)
    print(graph)


def _read_many(
    reader: Callable[[TextIO], Collection],
    *filenames: str,
) -> Collection:
    first, *rest = filenames
    with open(first) as f:
        collection = reader(f)
    for filename in rest:
        with open(filename) as f:
            collection = collection.merge(reader(f))
    return collection


@app.command()
def preprocess(
    output: str,
    wos: List[str] = typer.Option(help="WoS files to pre process"),
    scopus: List[str] = typer.Option(help="scopus files to preprocess"),
):
    """
    Preprocesses a collection.
    """
    wos_collection = _read_many(read_wos, *wos)
    scopus_collection = _read_many(read_scopus_ris, *scopus)
    p = Preprocess(wos_collection, scopus_collection)
    p.create_workbook(output)


if __name__ == "__main__":
    app()
