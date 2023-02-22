import bibtexparser
import pandas as pd
import networkx as nx

# type: ignore
def read_bib(bib_file_path):
    with open(bib_file_path, 'r', encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    df_scopus = pd.DataFrame(bib_database.entries)

    # Extract only numbers from the note column in scopus_df and convert to int type 
    df_scopus['note'] = df_scopus['note'].str.extract(r'(\d+)')

    # Change the name of the note column to 'times_cited'
    df_scopus.rename(columns={'note': 'times_cited'}, inplace=True)

    return df_scopus
