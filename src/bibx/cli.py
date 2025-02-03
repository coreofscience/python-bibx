import logging
from collections.abc import Callable
from enum import Enum
from typing import TextIO

import networkx as nx
import typer
from rich import print as rprint

from bibx import (
    query_openalex,
    read_any,
    read_scopus_bib,
    read_scopus_ris,
    read_wos,
)
from bibx.algorithms.preprocess import Preprocess
from bibx.algorithms.sap import Sap
from bibx.builders.openalex import HandleReferences
from bibx.collection import Collection

app = typer.Typer()


class Format(Enum):
    """Supported formats."""

    WOS = "wos"
    RIS = "ris"
    BIB = "bib"


@app.command()
def describe(format: Format, filename: str) -> None:
    """Parse a file and provides a short description."""
    if format == Format.WOS:
        with open(filename) as f:
            c = read_wos(f)
        rprint(":boom: the file satisfies the ISI WOS format")
        rprint(f"There are {len(c.articles)} records parsed")
    if format == Format.RIS:
        with open(filename) as f:
            c = read_scopus_ris(f)
        rprint(":boom: the file satisfies the ISI WOS format")
        rprint(f"There are {len(c.articles)} records parsed")
    if format == Format.BIB:
        with open(filename) as f:
            c = read_scopus_bib(f)
        rprint(":boom: the file satisfies the ISI WOS format")
        rprint(f"There are {len(c.articles)} records parsed")


@app.command()
def toy_sap() -> None:
    """Run the sap algorithm on a toy graph."""
    graph = nx.DiGraph()
    for node in "abcde":
        graph.add_node(node, year=2000)
    graph.add_edge("a", "b")
    for node in "cde":
        graph.add_edge("b", node)
    s = Sap()
    graph = s.tree(graph)
    rprint(graph)


@app.command()
def sap(filename: str) -> None:
    """Run the sap algorithm on a seed file of any supported format."""
    with open(filename) as f:
        collection = read_any(f)

    s = Sap()
    graph = s.create_graph(collection)
    graph = s.clean_graph(graph)
    graph = s.tree(graph)
    rprint(graph)


@app.command()
def openalex(
    query: list[str],
    references: HandleReferences = typer.Option(
        help="how to handle references",
        default=HandleReferences.BASIC,
    ),
    verbose: bool = typer.Option(
        help="be more verbose",
        default=False,
    ),
) -> None:
    """Run the sap algorithm on a seed file of any supported format."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    c = query_openalex(" ".join(query), references=references)
    s = Sap()
    graph = s.create_graph(c)
    graph = s.clean_graph(graph)
    graph = s.tree(graph)
    rprint(graph)


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
    wos: list[str] = typer.Option(help="WoS files to pre process"),
    scopus: list[str] = typer.Option(help="scopus files to preprocess"),
) -> None:
    """Preprocesses a collection."""
    wos_collection = _read_many(read_wos, *wos)
    scopus_collection = _read_many(read_scopus_ris, *scopus)
    p = Preprocess(wos_collection, scopus_collection)
    p.create_workbook(output)
    rprint(f":boom: workbook created at {output}")


if __name__ == "__main__":
    app()
