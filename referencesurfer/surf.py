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
from .paper_nodes import DAGNodeWrapper, Paper, PaperType
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
        return f"NewPaper with score = {self.score}"
    
    def message(self, paper, keywords, important_authors):
        print(f"""
        {self._score} paper score: {paper.get_title()} by {paper.get_first_author()}, 
        Total = {paper.score}, 
        Title = {paper.title_score(keywords)}, 
        Author = {paper.author_score(important_authors)} 
        """)
        

class PreviouslySeenPaper(SurfAction): 
    _is_back_to_start = False
    _is_jump = False

class LowScorePaper(SurfAction):
    _is_back_to_start = False
    _is_jump = True

    @staticmethod
    def message(paper, keywords, important_authors):
        print(f"""
        Very low paper score: {paper.get_title()} by {paper.get_first_author()}, 
        Total ={paper.score}, 
        Title = {paper.title_score(keywords)}, 
        Author = {paper.author_score(important_authors)} 
        - likely irrelevent, surf again
        """)

class StartingPaper(SurfAction): 
    _is_back_to_start = True
    _is_jump = False

class Surfer():
    def __init__(self, starting_papers, keywords = [], important_authors = [],
                 keyword_colours = {}):
        self.keywords = keywords
        self.important_authors = important_authors
        self.keyword_colours = keyword_colours
        self.paper_counter = dict()
        self.seen_DOIs = set()
        self.node_list = set()
        self.depth_list = dict()
        self.paired_node_list = dict()
        self.last_state = StartingPaper
        self.current_paper = None
        self.parent = None
        self.tree = set()
        self.jump = False
        
        self.graph = nx.MultiDiGraph()

        self.node_colours = dict()
        self.iterator_depth = 0
        
        if all([isinstance(p, Paper) for p in starting_papers]): 
            self.starting_papers = starting_papers
            for paper in self.starting_papers:
                paper.type = PaperType.STARTING_PAPER
                self.graph.add_node(paper)
                self.seen_DOIs.add(paper.get_DOI())
        else: 
            self.starting_papers = set()
            for doi in starting_papers: 
                try: 
                    query = query_from_DOI(doi)
                    paper = make_paper_from_query(query)
                    paper.type = PaperType.STARTING_PAPER
                    self.starting_papers.add(paper)
                    self.graph.add_node(paper)
                    self.seen_DOIs.add(paper.get_DOI())
                except Exception as e:
                    print(f"Unable to import paper {doi} into Surfer:")
                    print(e)
                    continue
                last_author = paper.get_last_author()
                last_author = unidecode(last_author)
                last_author = last_author.lower()
                if last_author not in important_authors:
                    important_authors.append(last_author)
                self.add_colours_to_node(paper)

        self.set_current_paper(self.starting_papers)

    def add_colours_to_node(self, paper): 
        for keyword in self.keyword_colours:
            if keyword in paper.get_title():
                paper.add_colour(self.keyword_colours[keyword])

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
            self.current_paper = papers[0]
        else: 
            self.current_paper = choice(list(papers))
    
    def iterate_surf(self, back_to_start_weight = 0.15):
        previous_paper = self.current_paper
        next_paper = self.next_paper(back_to_start_weight)
        if not self.last_state.is_jump():
            self.graph.remove_node(next_paper)
            next_paper.add_parent(previous_paper)
            self.graph.add_node(next_paper)
        return self.current_paper

    def next_paper(self, back_to_start_weight = 0.15):
        papers = list(self.graph.nodes)
        
        if not self.current_paper.get_references(): 
            print(f"Current paper does not have references on system: {self.current_paper.get_title()}")
            self.last_state = InvalidReferences
            self.set_current_paper(papers)
            self.iterator_depth = self.current_paper.depth
            return self.current_paper
        
        if random() < back_to_start_weight: 
            print(f"Gone back to the start..")
            self.last_state = BackToStart
            self.set_current_paper(self.starting_papers)
            # reset depth, which should always be 0 at this point
            self.iterator_depth = self.current_paper.depth
            if self.iterator_depth != 0:
                raise ValueError("Failsafe - gone back to start but depth != 0")
            self.parent = None
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
            
            if doi in self.seen_DOIs:
                print(f"Paper already seen: {random_paper.get_title()}")
                random_paper = next(n for n in list(self.graph.nodes) if n.get_DOI() == doi)
                
                # Update paper depth if shallower
                if self.iterator_depth < random_paper.depth:
                    random_paper.depth = self.iterator_depth
                    
                random_paper.counter += 1
                self.set_current_paper(random_paper)
                self.iterator_depth += 1
                self.last_state = PreviouslySeenPaper
                return self.current_paper
            
            if not isinstance(random_paper, DAGNodeWrapper):
                try: 
                    query = query_from_DOI(doi)
                except: 
                    print(f"Unable to get query for: {random_paper.get_title()}")
                    continue

                try:
                    random_paper = make_paper_from_query(query, depth = self.iterator_depth)
                    random_paper.type = PaperType.SURFED_PAPER
                except: 
                    print(f"Unable to make paper from query for: {random_paper.get_title()}")
                    continue
            
            ## set up new paper
            self.seen_DOIs.add(doi)
            random_paper.type = PaperType.SURFED_PAPER
            self.add_colours_to_node(random_paper)

            random_paper.score = random_paper.score_paper(self.keywords, self.important_authors)

            random_paper.counter += 1
            self.iterator_depth += 1
            self.graph.add_node(random_paper)
            self.set_current_paper(random_paper)
            self.last_state = NewPaper(score = random_paper.score)
            self.last_state.message(random_paper, self.keywords, self.important_authors)
            return self.current_paper
        
        self.set_current_paper(papers)
        self.iterator_depth = self.current_paper.depth
        self.last_state = InvalidReferences
        return self.current_paper

    def make_edges(self): 
        edges = []
        all_papers = list(self.graph.nodes)
        for paper in all_papers: 
            for parent in paper.get_parents():
                edge = (parent, paper)
                if edge not in edges:
                    edges.append(edge)
                    print(f"Parent: {edge[0].get_DOI()} child: {edge[1].get_DOI()}")
        self.graph.add_edges_from(edges)
        return edges
    
