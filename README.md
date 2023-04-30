# bibx

A python library with bibliographic and biblio-metric tools.

## Features

- Reads Web of Science (ISI) files.
- Reads scopus bibtex files.
- Merges scopus and ISI bibliographic collections.
- Implements the [SAP][sap] algorithm.
- More features in the roadmap...

## Example

Here's how to apply the sap algorithm:

```python
from bibx import read_scopus, Sap

with open('./docs/examples/scopus.bib') as f:
    c = read_scopus(f)
s = Sap()
g = s.create_graph(c)
g = s.clean_graph(g)
g = s.tree(g)
# Then work with g however you'd prefer
```

## References

- Zuluaga, M.; Robledo, S.; Arbelaez-Echeverri, O.; Osorio-Zuluaga, G. A. & Duque-Méndez, N. (2022). Tree of Science - ToS: A web-based tool for scientific literature recommendation. Search less, research more! _Issues In Science And Technology Librarianship_, 100. [https://dx.doi.org/10.29173/istl2696][web]
- Valencia-Hernandez, D. S., Robledo, S., Pinilla, R., Duque-Méndez, N. D., & Olivar-Tost, G. (2020). SAP Algorithm for Citation Analysis: An improvement to Tree of Science. _Ingeniería E Investigación_, 40(1), 45–49. [https://doi.org/10.15446/ing.investig.v40n1.77718][sap]
- Zuluaga, M.; Robledo, S.; Osorio-Zuluaga, G. A.; Yathe, L.; González, D. & Taborda, G. (2016). Metabolomics and pesticides: systematic literature review usinggraph theory for analysis of references. _Nova_, 14(25), 121-138. [https://dx.doi.org/10.22490/24629448.1735][meta]
- Robledo, S.; Osorio, G. & López, C. (2014). Networking en pequeña empresa: una revisión bibliográfica utilizando la teoria de grafos. _Revista Vínculos_, 11(2), 6-16. [https://dx.doi.org/10.14483/2322939X.9664][network]

[web]: https://dx.doi.org/10.29173/istl2696
[sap]: https://dx.doi.org/10.15446/ing.investig.v40n1.77718
[meta]: https://dx.doi.org/10.22490/24629448.1735
[network]: https://dx.doi.org/10.14483/2322939X.9664
