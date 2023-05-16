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
    abx_list, abx_colours, abx_classes = read_antibiotic_colours(ABX_COLOURS)
    abx_dict = {}
    for abx,colour in zip(abx_list, abx_colours):
        abx_dict[abx] = colour

    surfer = Surfer(starting_DOIs, keywords, important_authors, abx_dict)

    #paper_lag = surfer.current_paper
    #Start surfing
    for _ in range(10): 
        print(f"iteration {_}")
        new_paper = surfer.iterate_surf()
        print(f"******{new_paper}")
        """
        new_paper_name = new_paper.make_name()
        new_node = DAGNode(new_paper_name)
        if new_node not in surfer.node_list:
            surfer.node_list.add(new_node)
        """

        """
        #If current paper has been arrived at from another paper without jumping - set parent and increase depth
        print(surfer.last_state)
        if not surfer.last_state.is_jump(): 
            parent_name = paper_lag.make_name()
            new_node.set_parent(parent_name)
            parent_depth = surfer.depth_list[parent_name]
            new_depth = parent_depth + 1
            new_node.set_depth(new_depth)
            new_node_depth = new_node.get_depth()
            surfer.depth_list[new_paper_name] = new_node_depth
            new_edge = new_node.make_scoreless_edge()
            if new_paper_name not in surfer.paired_node_list:
                surfer.paired_node_list[new_paper_name] = []
                surfer.paired_node_list[new_paper_name].append(new_edge)
            else:
                if new_edge not in surfer.paired_node_list[new_paper_name]:
                    surfer.paired_node_list[new_paper_name].append(new_edge)
                else:
                    pass
        """
        
        """
        #Assign a colour
        new_paper_title = new_paper.get_title()
        if new_paper_name not in surfer.node_colours:
            surfer.node_colours[new_paper_name] = []
            for ab in abx_list:
                if ab in new_paper_title:
                    surfer.node_colours[new_paper_name].append(abx_colours[ab])
        else:
            for ab in abx_list:
                if ab in new_paper_title:
                    surfer.node_colours[new_paper_name].append(abx_colours[ab])
        
        """
        """
        #Keep track of how many times we have seen this paper
        if new_paper not in surfer.starting_papers: 
            if new_paper not in surfer.seen_papers: 
                surfer.paper_counter[new_paper] = 1
                surfer.seen_DOIs.add(new_paper.get_DOI())
                surfer.seen_papers.add(new_paper)
            else: 
                surfer.paper_counter[new_paper] += 1
     
        """
        # I don't think these steps are necessary 
        # there is already a check in iterate_surf
        
        """
        if new_paper.get_references(): 
            paper_lag = new_paper
        elif surfer.seen_papers: 
            paper_lag = choice(list(surfer.seen_papers))
        else: 
            paper_lag = choice(list(surfer.starting_papers))
        """
        

    #Print our list of papers and how many times we have seen them, in order of frequency   
    #sorted_paper_counter = sorted(surfer.paper_counter.items(), key=lambda item: item[1], reverse=True)
    sorted_papers = sorted(list(surfer.graph.nodes), key = lambda paper: paper.counter, reverse=True)

    for paper in sorted_papers: 
        print(f"Paper {paper.make_name()} {paper.get_title()} DOI {paper.get_DOI()} seen {paper.counter} times")
    """
        #Make pairs for DAG edges
        concat_paired_nodes = []
        for paper_name in surfer.paired_node_list:
            for pair in surfer.paired_node_list[paper_name]:
                concat_paired_nodes.append(pair)
    """
    
    edges = surfer.make_edges()
    nodes = list(surfer.graph.nodes)
    labels = {paper: paper.get_DOI() for paper in list(surfer.graph)}
    DAG = surfer.graph
    nx.draw_networkx(DAG, labels = labels)
    plt.show()
    print(labels)
    pos= nx.nx_agraph.graphviz_layout(DAG, prog = "dot")
    nx.draw_networkx_nodes(DAG, pos)
    nx.draw_networkx_edges(DAG, pos, alpha=0.4, arrowstyle='<|-')
    nx.draw_networkx_labels(DAG, labels)
    plt.show()
    #Make labels for DAG nodes - label all initial papers
    labelled_list = [] 
    labels = {}
    node_name_list = []
    for paper in surfer.starting_papers:
        papername = paper.make_name() 
        labelled_list.append(papername)
    print(f"labelled starting {labelled_list}")
    for node in surfer.node_list:
        name = node.get_name() 
        node_name_list.append(name)
    
    #Calculate scores for DAG node size
    freq_list = {}
    score_list = {}
    for paper, frequency in surfer.paper_counter.items():
        id = paper.make_name()
        freq_list[id] = frequency
    for pap_name in node_name_list:
        if pap_name in freq_list:
            freq_score = freq_list[pap_name]
        else:
            freq_score = 1
        if pap_name in surfer.depth_list and surfer.depth_list[pap_name] != None: 
            depth_score = surfer.depth_list[pap_name]
            depth_score = depth_score * 3
        else:
            depth_score = 0
        score = (freq_score + depth_score)
        score_list[pap_name] =  score

    #Colour DAG nodes according to antibiotic
    colour_list = dict()
    for paper_name in surfer.node_colours:
        collist = []
        for col in surfer.node_colours[paper_name]:
            collist.append(col)
        if len(collist) == 0:
            colour_list[paper_name] = '#ADACAC'
        elif len(collist) == 1:
            colour_list[paper_name] = collist[0]
        else:
            colset = set(surfer.node_colours[paper_name])
            if len(collist) != len(colset):
               colsetlist = list(colset)
               if len(colsetlist) > 1:
                    colour_list[paper_name] = '#D8C292'
               else:
                    colour_list[paper_name] = colsetlist[0]

    for paper_name in node_name_list:
        if paper_name not in colour_list.keys():
            colour_list[paper_name] = '#ADACAC'

    #Make starting papers look different
    alpha_list = dict()
    line_width_list = {}
    for paper in surfer.starting_papers:
        name = paper.make_name()
        alpha_list[name] = 0.7
        line_width_list[name] = 7
    for paper_name in node_name_list:
        if paper_name not in alpha_list:
            alpha_list[paper_name] = 0.9
        if paper_name not in line_width_list:
            line_width_list[paper_name] = 2

    #Add elements to the the DAG
    DAG = nx.MultiDiGraph()
    DAG.add_nodes_from(node_name_list)
    nx.set_node_attributes(DAG, score_list, 'size')
    nx.set_node_attributes(DAG, colour_list, 'color')
    nx.set_node_attributes(DAG, alpha_list, 'alpha')
    nx.set_node_attributes(DAG, line_width_list, 'line_width')
    nx.set_node_attributes(DAG, node_name_list, 'name')
    DAG.add_edges_from(concat_paired_nodes)
    
    #Adjust score list to create DAG node sizes
    for i in score_list:
        score_list[i] *= 20
        #n = float(DAG.number_of_nodes())
        #score_list[i] += ((300/n)*100)

    #Draw DAG    
    pos= nx.nx_agraph.graphviz_layout(DAG, prog = "dot")
    nx.draw_networkx_nodes(DAG, pos, 
                           node_size=[score_list[n] for n in DAG.nodes()], 
                           node_color=[colour_list[n] for n in DAG.nodes()], 
                           alpha=[alpha_list[n] for n in DAG.nodes()], 
                           linewidths=[line_width_list[n] for n in DAG.nodes()])
    nx.draw_networkx_edges(DAG, pos, alpha=0.4, arrowstyle='<|-')
    
    #Pring nodes with highest incoming edges (i.e. most referenced)
    in_values = dict()
    top_cited = dict()
    for n in DAG.nodes:
        in_value = DAG.out_degree(n)
        in_values[n] = f"{in_value}"
    top_cited = sorted(in_values.items(), key=lambda item: item[1], reverse=True)[:10]
    print(f"TOP CITED:")
    for key,value in sorted(top_cited, key=lambda item: item[1], reverse=True):
         print(f"Paper {key} cited {value} times")   

    #Make more labels for DAG Nodes - label all highly cited papers
    
    for n in DAG.nodes:
        citedness = DAG.out_degree(n)
        if citedness >= 3:
            if n not in labelled_list:
                labelled_list.append(n)
    
    #ALTERNATIVE TO DECIDING TOP SITED FOR LABELLING#
    """
    for n in top_cited:
        if n not in labelled_list:
            labelled_list.append(n)
    """
    for name in labelled_list:
            labels[name] = f"{name}" 

    nx.draw_networkx_labels(DAG, pos = nx.nx_agraph.graphviz_layout(DAG, prog = "dot"), 
                            labels = {n:lab for n,lab in labels.items() if n in pos}, 
                            font_size=6, font_weight='bold', font_family='sans-serif', 
                            horizontalalignment = 'center', verticalalignment = 'center')

    write_output(OUTPUT_PATH, surfer.paper_counter)
    
    plt.show()

main()
