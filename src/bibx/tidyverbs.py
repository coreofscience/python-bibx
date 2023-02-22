import bibtexparser
import pandas as pd
import networkx as nx

# type: ignore
def scopus_graph(bib_file_path):
    with open(bib_file_path, 'r', encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    df = pd.DataFrame(bib_database.entries)
    df['SR'] = df['author'].str.split('and').str[0].str.replace(r'[^\w\s]+', '').str.upper().str.strip() + ', ' + df['year']
    df2 = df[['SR', 'references']]
    df2 = df2.set_index(['SR'])['references'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='references')
    df2['SR2'] = df2['references'].str.split(',', 2).str[0].str.replace(r'[^\w\s]+', '').str.upper().str.strip() + ','
    df2['year'] = df2['references'].str.extract(r'(\d{4})')
    df2['SR3'] = df2['SR2'] + ' ' + df2['year']
    df2['SR_1'] = df2['SR'].str.split(',', 2).str[0].str.replace(r'[^\w\s]+', '').str.upper().str.strip() + ','
    df3 = df2[['SR', 'SR3']]
    df3.columns = ['SR', 'CR']

    G = nx.DiGraph()
    G.add_edges_from(df3.values)
    largest_scc = max(nx.strongly_connected_components(G), key=len)
    Gc = G.subgraph(largest_scc).copy()
    Gc.remove_nodes_from([n for n in Gc if Gc.in_degree(n) == 1 and Gc.out_degree(n) == 0])
    Gc.remove_edges_from(nx.selfloop_edges(Gc))

    return Gc
