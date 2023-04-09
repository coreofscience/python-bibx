# Welcome to bibx

A library for scientific bibliography parsing and processing.

## Example

```python
from bibx import read_scopus
from bibx.algorithms.sap import Sap

with open("your/scopus/bibtex/file.bib") as f:
    collection = read_scopus(f)

graph = Sap.create_graph(collection)
graph = Sap.clean_graph(graph)
sap = Sap()
graph = sap.tree(graph)
```
