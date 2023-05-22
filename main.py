#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	main.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-03-24
# Copyright: 	Alessandro Gerada, Nada Reza 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""Documentation"""

# External dependencies
from habanero import Crossref
from Bio import Entrez
from metapub import PubMedFetcher
import urllib.request
from urllib.error import HTTPError
import csv
from datetime import datetime
from random import random, choice
from anytree import Node, RenderTree
from unidecode import unidecode
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx 
from matplotlib.patches import FancyArrowPatch
import metapub
from networkx.drawing.nx_agraph import graphviz_layout as graphviz_layout

# Internal dependencies
from referencesurfer.surf import Surfer, BackToStart, InvalidReferences, NewPaper, PreviouslySeenPaper, LowScorePaper
from referencesurfer.paper_nodes import DAGNode
from referencesurfer.data_processing import read_keywords, read_imported_authors
from referencesurfer.data_processing import read_starting_corpus, read_keyword_colours
from referencesurfer.data_processing import write_output
from referencesurfer.query_handlers import query_from_DOI, make_paper_from_query
from tests.surfing_test import make_test_corpus

Entrez.email = 'youremail@email.com'
NCBI_API_KEY='your_API_key'
#into terminal: export NCBI_API_KEY='YOUR API-KEY'

KEYWORDS_PATH = 'referencesurfer/keywords.csv'
IMPORTANT_AUTHORS_PATH = 'referencesurfer/important_authors.csv'
STARTING_CORPUS_PATH = 'referencesurfer/corpus.csv'
KEYWORD_COLOURS = 'referencesurfer/antibiotic_colours.csv'
OUTPUT_PATH = 'output.csv'

def main(): 
    keywords = read_keywords(KEYWORDS_PATH)
    important_authors = read_imported_authors(IMPORTANT_AUTHORS_PATH)
    starting_DOIs = read_starting_corpus(STARTING_CORPUS_PATH)
    colour_dict = read_keyword_colours(KEYWORD_COLOURS)

    _, starting_papers = make_test_corpus()

    surfer = Surfer(starting_papers, keywords, important_authors, colour_dict)

    for _ in range(1000): 
        surfer.iterate_surf()
        
    print(surfer)
    surfer.draw_graph()
    plt.show()

    write_output(OUTPUT_PATH, list(surfer.graph))

main()
