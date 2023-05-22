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
from referencesurfer.data_processing import read_starting_corpus, read_antibiotic_colours
from referencesurfer.data_processing import write_output
from referencesurfer.query_handlers import query_from_DOI, make_paper_from_query
from tests.surfing_test import make_test_corpus

Entrez.email = 'youremail@email.com'
NCBI_API_KEY='your_API_key'
#into terminal: export NCBI_API_KEY='YOUR API-KEY'

KEYWORDS_PATH = 'referencesurfer/keywords.csv'
IMPORTANT_AUTHORS_PATH = 'referencesurfer/important_authors.csv'
STARTING_CORPUS_PATH = 'referencesurfer/corpus.csv'
ABX_COLOURS = 'referencesurfer/antibiotic_colours.csv'
OUTPUT_PATH = 'output.csv'

def main(): 
    keywords = read_keywords(KEYWORDS_PATH)
    important_authors = read_imported_authors(IMPORTANT_AUTHORS_PATH)
    starting_DOIs = read_starting_corpus(STARTING_CORPUS_PATH)
    
    #Colour nodes by antibiotic class
    abx_dict = read_antibiotic_colours(ABX_COLOURS)

    _, starting_papers = make_test_corpus()

    surfer = Surfer(starting_papers, keywords, important_authors, abx_dict)

    #paper_lag = surfer.current_paper
    #Start surfing
    for _ in range(1000): 
        surfer.iterate_surf()

    #Print our list of papers and how many times we have seen them, in order of frequency   
    #sorted_paper_counter = sorted(surfer.paper_counter.items(), key=lambda item: item[1], reverse=True)
    sorted_papers = sorted(list(surfer.graph.nodes), key = lambda paper: paper.counter, reverse=True)

    for paper in sorted_papers: 
        print(f"Paper {paper.get_DOI()} {paper.get_title()} DOI {paper.get_DOI()} seen {paper.counter} times")

    surfer.make_edges()
    labels = {paper: paper.get_DOI() for paper in list(surfer.graph)}
    DAG = surfer.graph
    pos= nx.nx_agraph.graphviz_layout(DAG, prog = "dot")

    # sizes
    node_scores = [n.score + n.counter for n in list(surfer.graph) if not n.is_starting_paper()]
    mean_node_score = np.mean(node_scores)
    node_size_multiplier = [(n.score + n.counter) / mean_node_score if not n.is_starting_paper() else 1
                            for n in list(surfer.graph)]
    node_size = [i * 300 for i in node_size_multiplier]
    
    # colours
    node_colours = {}
    for n in list(surfer.graph):
        if n.is_starting_paper():
            node_colours[n] = '#2986CC'
        elif n.score + n.counter > mean_node_score:
            node_colours[n] = '#00FF00'
        else: 
            node_colours[n] = '#F44336'

    nx.draw_networkx(DAG, pos, labels = labels, node_size = node_size, node_color = node_colours.values())
    plt.show()
    write_output(OUTPUT_PATH, list(surfer.graph))

main()
