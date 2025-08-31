import logging
from enum import Enum
from typing import Annotated

import networkx as nx
import typer
from rich import print as rprint

from bibx import (
    query_openalex,
    read_any,
    read_scopus_bib,
    read_scopus_csv,
    read_scopus_ris,
    read_wos,
)
from bibx.algorithms.sap import Sap
from bibx.sources.openalex import EnrichReferences

app = typer.Typer()


@app.callback()
def set_verbose(
    verbose: Annotated[  # noqa: FBT002
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging.")
    ] = False,
) -> None:
    """BibX is a command-line tool for parsing bibliographic data."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)


class Format(Enum):
    """Supported formats."""

    WOS = "wos"
    RIS = "ris"
    BIB = "bib"
    CSV = "csv"


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
        rprint(":boom: the file satisfies the scopus RIS format")
        rprint(f"There are {len(c.articles)} records parsed")
    if format == Format.BIB:
        with open(filename) as f:
            c = read_scopus_bib(f)
        rprint(":boom: the file satisfies the scopus BIB format")
        rprint(f"There are {len(c.articles)} records parsed")
    if format == Format.CSV:
        with open(filename) as f:
            c = read_scopus_csv(f)
        rprint(":boom: the file satisfies the scopus CSV format")
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
    enrich: EnrichReferences = typer.Option(
        help="how to handle references",
        default=EnrichReferences.BASIC,
    ),
) -> None:
    """Run the sap algorithm on a seed file of any supported format."""
    c = query_openalex(" ".join(query), enrich=enrich)
    s = Sap()
    graph = s.create_graph(c)
    graph = s.clean_graph(graph)
    graph = s.tree(graph)
    rprint(graph)


@app.command()
def csv(filename: str) -> None:
    """Parse a scopus CSV file and print the collection."""
    with open(filename) as f:
        c = read_scopus_csv(f)
    rprint(list(c.citation_pairs))


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    app()
