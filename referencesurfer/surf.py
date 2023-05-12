#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	filename.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-04-25
# Copyright: 	Alessandro Gerada 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""Surfing classes"""
import os
import sys
from random import random,choice
from unidecode import unidecode
import networkx as nx 

# Internal dependencies
from .paper_nodes import DAGNode, Paper
from .data_processing import read_keywords, read_imported_authors
from .data_processing import read_starting_corpus, read_antibiotic_colours
from .data_processing import write_output
from .query_handlers import query_from_DOI, make_paper_from_query

class SurfAction:
    def __init__(self): 
        pass
    
    @classmethod
    def is_back_to_start(cls): 
        return cls._is_back_to_start
    
    @classmethod
    def is_jump(cls):
        return cls._is_jump
    
class BackToStart(SurfAction): 
    _is_back_to_start = True
    _is_jump = True

class InvalidReferences(SurfAction): 
    _is_back_to_start = False
    _is_jump = True

class NewPaper(SurfAction): 
    _is_back_to_start = False
    _is_jump = False
    def __init__(self, score): 
        self._score = score
        super().__init__()
    
    def __repr__(self): 
        return f"NewPaper with {self._score} score"

class PreviouslySeenPaper(SurfAction): 
    _is_back_to_start = False
    _is_jump = False

class LowScorePaper(SurfAction):
    _is_back_to_start = False
    _is_jump = False

class StartingPaper(SurfAction): 
    _is_back_to_start = None
    _is_jump = None

class Surfer():
    def __init__(self, starting_papers, keywords = [], important_authors = [],
                 abx_colors = {}):
        self.seen_papers = set()
        self.keywords = keywords
        self.important_authors = important_authors
        self.abx_colours = abx_colors
        self.paper_counter = dict()
        self.seen_DOIs = set()
        self.node_list = set()
        self.depth_list = dict()
        self.paired_node_list = dict()
        self.last_state = StartingPaper
        
        self.graph = nx.MultiDiGraph()

        self.node_colours = dict()
        self.iterator_depth = 0
        
        if all([type(p) == Paper for p in starting_papers]): 
            self.starting_papers = starting_papers
        else: 
            self.starting_papers = set()
            for doi in starting_papers: 
                try: 
                    query = query_from_DOI(doi)
                    paper = make_paper_from_query(query)
                    self.starting_papers.add(paper)
                    self.graph.add_node(paper, parents = (), 
                                        depth = None, 
                                        score = None)
                except Exception as e:
                    print(f"Unable to import paper {doi} into Surfer:")
                    print(e)
                try: 
                    last_author = paper.get_last_author()
                    last_author = unidecode(last_author)
                    last_author = last_author.lower()
                    if last_author not in important_authors:
                        important_authors.append(last_author)
                except: 
                    pass

                for ab in self.abx_colours:
                    if ab in paper.get_title():
                        paper.add_colour(abx_colors[ab])

        self.set_current_paper(self.starting_papers)

    def set_current_paper(self, papers): 
        """
        Sets current paper
        If more than one paper provided, randomly choose 
        """
        
        if not papers: 
            raise ValueError("No starting paper provided")
        
        if isinstance(papers, Paper): 
            self.current_paper = papers
        elif len(papers) == 1: 
            [self.current_paper] = papers
        else: 
            self.current_paper = choice(list(papers))

    def iterate_surf(self, back_to_start_weight = 0.15):
        if self.seen_papers:
            papers = self.seen_papers.union(self.starting_papers)
        else:
            papers = self.starting_papers
        
        if not self.current_paper.get_references(): 
            print(f"Current paper does not have references on system: {self.current_paper.get_title()}")
            self.last_state = InvalidReferences
            self.set_current_paper(papers)
            return self.current_paper
        
        if random() < back_to_start_weight: 
            self.last_state = BackToStart
            self.set_current_paper(self.starting_papers)
            return self.current_paper
        
        for _ in range(10): 
            random_paper = choice(self.current_paper.get_references())

            # if we have already seen paper, don't download again

            doi = random_paper.get_DOI()
            if not doi: 
                if not random_paper.get_title(): 
                    print("Empty paper title and empty DOI")
                else:
                    print(f"No DOI for {random_paper.get_title()} found")
                continue
            
            if doi not in self.seen_DOIs:
                try: 
                    query = query_from_DOI(doi)
                except: 
                    print(f"Unable to get query for: {random_paper.get_title()}")
                    continue

                try:
                    random_paper = make_paper_from_query(query)
                except: 
                    print(f"Unable to make paper from query for: {random_paper.get_title()}")
                    continue

                self.seen_DOIs.add(doi)
                self.seen_papers.add(random_paper)
                list_of_nodes = list(self.graph.nodes)
                if random_paper in list_of_nodes:
                    # already seen
                    old_node = next(n for n in list_of_nodes if n == random_paper)
                    # update depth if SHALLOWER
                    random_paper = random_paper if random_paper.depth < old_node.depth else old_node
                    self.graph.add_node(random_paper)
                random_paper.add_parent(self.current_paper)
                random_paper_score = random_paper.score_paper(self.keywords, self.important_authors)

                if random_paper_score <= 10:
                    print(f"""
                    Very low paper score: {random_paper.get_title()} by {random_paper.get_first_author()}, 
                    Total ={random_paper_score}, 
                    Title = {random_paper.title_score(self.keywords)}, 
                    Author = {random_paper.author_score(self.important_authors)} 
                    - likely irrelevent, surf again
                    """)

                    back_to_start_weight = 0.15 # is this used? function returns just after
                    self.set_current_paper(papers)
                    self.last_state = LowScorePaper
                    return self.current_paper
        
                elif 10 < random_paper_score < 20:
                    print(f"""
                    Moderate paper score: {random_paper.get_title()} by {random_paper.get_first_author()}, 
                    Total = {random_paper_score}self., 
                    Title = {random_paper.title_score(self.keywords)}, 
                    Author = {random_paper.author_score(self.important_authors)} 
                    - may be relevant, accept paper but increase BTS 
                    """)
                    
                    back_to_start_weight = 0.8 # same here, will be overwritten on next function call
                    self.set_current_paper(random_paper)
                    self.update_counter(random_paper)
                    self.last_state = NewPaper(score="moderate")
                    return self.current_paper
                
                elif random_paper_score > 40:
                    print(f"""
                    Excellent paper score: {random_paper.get_title()} by {random_paper.get_first_author()}, 
                    Total ={random_paper_score}, 
                    Title = {random_paper.title_score(self.keywords)}, 
                    Author = {random_paper.author_score(self.important_authors)} 
                    - highly likely relevant as are subsequent references, reduce BTS
                    """)
                    
                    back_to_start_weight = 0.05 # ditto
                    self.set_current_paper(random_paper)
                    self.update_counter(random_paper)
                    self.last_state = NewPaper(score="excellent")
                    return self.current_paper
                
                else:
                    print(f"""Good paper score: {random_paper.get_title()} by {random_paper.get_first_author()}, Total ={random_paper_score}, Title = {random_paper.title_score(self.keywords)}, Author = {random_paper.author_score(self.important_authors)} - likely relevant, continue""")
                    back_to_start_weight = 0.15 # ditto
                    self.set_current_paper(random_paper)
                    self.update_counter(random_paper)
                    self.last_state = NewPaper(score="good")
                    return self.current_paper


            else: 
                print(f"Paper already seen: {random_paper.get_title()}")
                random_paper = next(x for x in self.seen_papers if x.get_DOI() == doi)
                self.set_current_paper(random_paper)
                self.update_counter(random_paper)
                self.last_state = PreviouslySeenPaper
                return self.current_paper
        
        self.set_current_paper(papers)
        self.last_state = PreviouslySeenPaper
        return self.current_paper
    
    def update_counter(self, paper): 
        if paper in self.paper_counter:
            self.paper_counter[paper] += 1
        else: 
            self.paper_counter[paper] = 1
