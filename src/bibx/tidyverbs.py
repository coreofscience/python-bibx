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

# type: ignore
def read_bib(bib_file_path):
    with open(bib_file_path, 'r', encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    df_scopus = pd.DataFrame(bib_database.entries)

    # Extract only numbers from the note column in scopus_df and convert to int type 
    df_scopus['note'] = df_scopus['note'].str.extract(r'(\d+)')

    # Change the name of the note column to 'times_cited'
    df_scopus.rename(columns={'note': 'times_cited'}, inplace=True)

    # Creating a new column called 'id_scopus
    df_scopus['id_scopus'] = df_scopus['author'].str.split('and').str[0].str.replace(r'[^\w\s]+', '').str.upper().str.strip() + ', ' + df_scopus['year']
    

    return df_scopus

def get_references_edgelist(df):
    df['reference_format'] = df['author'].str.replace(r'[^\w\s]+', '').str.upper().str.strip() + ', ' + df['title'] + '. (' + df['year'] + ') ' + df['journal'] + ', pp. ' + df['pages']
    # select the columns 'id_scopus', 'reference_format', and 
    # 'references' and assign it to a new dataframe called 'references_df'
    #
    # Hint: Use the 'loc' function to select the columns
    #
    references_df = df.loc[:, ['id_scopus', 'reference_format', 'references']]

    # Remove the rows that have NaN values in the 'references' column
    #
    # Hint: Use the 'dropna' function
    #
    references_df = references_df.dropna(subset=['references'])

    # Remove the rows that have NaN values in the 'reference_format' column
    #
    # Hint: Use the 'dropna' function
    #
    references_df = references_df.dropna(subset=['reference_format'])

    # Remove the rows that have NaN values in the 'id_scopus' column
    #
    # Hint: Use the 'dropna' function
    #
    references_df = references_df.dropna(subset=['id_scopus'])

    references_df_1 = references_df.set_index(['id_scopus'])['references'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='references')

    # Remove the rows that have NaN values in the 'references' column
    #
    # Hint: Use the 'dropna' function
    #
    references_df_1 = references_df_1.dropna(subset=['references'])

    # remove 'references' from the references_df dataframe
    #
    # Hint: Use the 'drop' function
    #
    references_df = references_df.drop(columns=['references'])

    # Merge the 'references_df' and 'references_df_1' dataframes on the 'id_scopus' column 
    # and assign it to a new dataframe called 'references_df_2'
    #
    # Hint: Use the 'merge' function
    #
    references_df_2 = pd.merge(references_df, references_df_1, on='id_scopus')
    
    references_df_2['id_scopus2'] = references_df_2['references'].str.split(',', 2).str[0].str.replace(r'[^\w\s]+', '').str.upper().str.strip() + ','
    references_df_2['year'] = references_df_2['references'].str.extract(r'(\d{4})')
    references_df_2['id_scopus3'] = references_df_2['id_scopus2'] + ' ' + references_df_2['year']
    references_df_2['id_scopus_1'] = references_df_2['id_scopus'].str.split(',', 2).str[0].str.replace(r'[^\w\s]+', '').str.upper().str.strip() + ','

    # Select the columns 'id_scopus', 'id_scopus_3', 'reference_format', and 'references'
    # and assign it to a new dataframe called 'references_df_3'
    #
    # Hint: Use the 'loc' function to select the columns
    #
    references_df_3 = references_df_2.loc[:, ['id_scopus', 'id_scopus3', 'reference_format', 'references']]

    # Remove duplicates from the 'references_df_3' dataframe
    #
    # Hint: Use the 'drop_duplicates' function
    #
    references_df_3 = references_df_3.drop_duplicates()

    # Rename the 'id_scopus_3' column to 'id_scopus', 'id_scopus_3' column to 'id_reference', 
    # 'reference_format' column to 'title_source', and 'references' column to 'title_target'
    # 
    # Hint: Use the 'rename' function
    # 
    references_df_3 = references_df_3.rename(columns={'id_scopus3': 'id_reference', 'reference_format': 'title_source', 'references': 'title_target'})    

    # Transfrom to upper case all columns in the 'references_df_3' dataframe
    #
    # Hint: Use the 'upper' function
    #
    references_df_3 = references_df_3.apply(lambda x: x.astype(str).str.upper())

    return references_df_3

def get_tos_graph(scopus_edgelist):
    # Create a new dataframe called 'scopus_edgelist' that contains the 
    # 'id_scopus' and 'id_reference' columns from the 'scopus_edgelist' dataframe
    #
    # Hint: Use the 'loc' function to select the columns
    #
    scopus_edgelist = scopus_edgelist.loc[:, ['id_scopus', 'id_reference']]
    # create a directed graph object called 'G' using the 'scopus_edgelist' dataframe 
    # and assign it to a new dataframe called 'G'
    #
    # Hint: Use the 'from_pandas_edgelist' function
    #
    G = nx.DiGraph()
    G.add_edges_from(scopus_edgelist.values)
    # Remove the edges that have self-loops from the graph object 'G'
    #
    # Hint: Use the 'remove_edges_from' function
    #
    G.remove_edges_from(nx.selfloop_edges(G))
    # Remove the nodes that have in-degree equal to 1 and out-degree equal to 0
    # from the graph object 'G'
    #
    # Hint: Use the 'remove_nodes_from' function
    #
    G.remove_nodes_from([n for n in G if G.in_degree(n) == 1 and G.out_degree(n) == 0])

    return G
