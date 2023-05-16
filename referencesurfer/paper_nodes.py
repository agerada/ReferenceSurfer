#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	Paper.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-04-25
# Copyright: 	Alessandro Gerada 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""Paper and PaperNode classes"""

from anytree import NodeMixin
import networkx as nx 
from unidecode import unidecode
import warnings

class Paper:
    def __init__(self, DOI, title, author, year, references = None):
        self._DOI = DOI
        self._title = title
        self._author = author
        self._year = year
        self._name = self.make_name()
        self._references = []
        if references:
            self.add_references(references)
    
    def add_references(self, references):
        for i in references:
            doi = i['DOI'] if 'DOI' in i else None
            title = i['article-title'] if 'article-title' in i else None
            author = i['author'] if 'author' in i else None
            year = i['year'] if 'year' in i else None
            ref = Paper(doi, title, author, year)
            self._references.append(ref)                     
    
    def set_references(self, references: list):
        if not all(True for ref in references if isinstance(ref, Paper)):
            raise TypeError("Trying to set references with non Paper objects")
        else: 
            self._references = references

    def __repr__(self) -> str:
        return f"""
        Paper {self._DOI}, author: {self.get_first_author()}, year: {self._year},
        title: {self._title}
        {len(self._references)} references
        """
    
    def __hash__(self): 
        return hash(self._DOI)
    
    def __eq__(self, other):
        if isinstance(other, Paper): 
            return self._DOI == other._DOI
        return NotImplemented
    
    def get_first_author(self): 
        try: 
            author = self._author[0]['family']
        except: 
            author = None
        return author
    
    def get_last_author(self):
        try:
            author = self._author[-1]['family']
        except:
            author = None
        return author
    
    def get_all_authors(self):
        try: 
            authors_list = []
            for author in self._author:
                if author != self._author[0] & author != self._author[-1]:
                    family_name = author['family']
                    authors_list.append[family_name]
        except:
            author = None
        return authors_list
    
    def get_references(self):
        return self._references
    
    def get_title(self): 
        return self._title
    
    def get_DOI(self):
        return self._DOI
    
    def change_data(self, data: dict = {}): 
        if not data: 
            return
        accepted_fields = ('title', 'doi', 'author', 'year', 'references')
        for k,v in data.items(): 
            if k.lower() in accepted_fields:
                match k.lower(): 
                    case 'title': 
                        self._title = v
                    case 'doi': 
                        self._DOI = v
                    case 'author': 
                        self._author = v
                    case 'year': 
                        self._year = v
                    case 'references': 
                        self._references = v
            else:
                raise KeyError('invalid data provided to Paper.change_data()')


    def get_year(self):
        return self._year   
    
    def make_name(self):
        name = f""" \n {self.get_first_author()} \n {self.get_year()}""" 
        {self.get_DOI()} 
        return name
    
    def title_score(self, keywords):
        title = self.get_title()
        title_score = float(0)
        if title:  
            title = unidecode(title)
            title = title.lower()
            for keyword in keywords: 
                if keyword[0] in title:
                    value = float(keyword[1])
                    title_score = title_score + value
            return title_score
        else:
            title_score = float(0)
    
    def author_score(self, important_authors):
        first_author = self.get_first_author()
        last_author = self.get_last_author()
        all_authors = self.get_all_authors()
        author_score = float(0)

        if first_author:
            first_author = unidecode(first_author)
            first_author = first_author.lower()
            for author in important_authors:
                if author in first_author:
                    author_score = author_score + (25 * 0.375)
        else:
            author_score = float(0)
        if last_author:
            last_author = unidecode(last_author)
            last_author = last_author.lower()
            for author in important_authors:
                if author in last_author:
                    author_score = author_score + (25 * 0.375)
        else:
            author_score = float(0)
        if all_authors:
            for author in all_authors[:25]:
                author = unidecode(author)
                author = author.lower()
            if author in all_authors:
                author_score = author_score + (1 * 0.25)
        else:
            author_score = float(0)
        if author_score > 25:
            author_score = float(25)
        return(author_score)
    
    def score_paper(self, keywords, important_authors):
        if self.title_score(keywords):
            wt_title_score = float(3 * self.title_score(keywords))
        else:
            wt_title_score = float(0)
        author_score = self.author_score(important_authors)
        paper_score = (wt_title_score + author_score)
        return(paper_score)

class DAGNode:
    def __init__(self, name, parent: Paper = None, depth = None, score = None):
        warnings.warn("DAGNode class is deprecated", DeprecationWarning, 2)
        if name is not None:
            self._name = name
            DeprecationWarning
        if isinstance(parent, Paper):
            self._parent = parent.make_name()
        if score is not None:
            self._score = score
        if depth is not None:
            self._depth = depth
    
    def set_parent(self, parent_name): 
        self._parent = parent_name
    
    def get_parent(self): 
        return self._parent
    
    def get_name(self):
        return self._name
    
    def set_depth(self, depth):
        self._depth = depth
    
    def get_depth(self):
        return self._depth

    def make_scoreless_edge(self):
        parent = f"{self._parent}"
        name = f"{self._name}"
        dag_edge = (name, parent)
        return(tuple(dag_edge))

    def set_score(self, score):
        self._score = score
        return(self._score)   
    
    def make_scored_edge(self):
        parent = f"{self._parent}"
        name = f"{self._name}"
        score = self._score
        dag_edge = (name, parent, score)
        return(tuple(dag_edge))    

class DAGNodeWrapper(Paper):
    def __init__(self, DOI, title, author, year, 
                 references = None, 
                 parents = frozenset(), 
                 depth = 0, 
                 score = 0, 
                 colours = set(),
                 counter = 0):
        self.set_parents(parents)
        self.counter = counter
        self.depth = depth
        self.score = score
        self._colours = colours
        super().__init__(DOI, title, author, year, references)
    
    def set_parents(self, parents: frozenset[Paper]): 
        if not isinstance(parents, frozenset): 
            raise ValueError("Input to DAGNodeWrapper.set_parents() not recognised")
        if not all(True for paper in parents if isinstance(paper, Paper)): 
            raise ValueError("Input to DAGNodeWrapper.set_parents() not recognised")
        self._parents = parents
    
    def add_parent(self, new_parent): 
        old_parents = self._parents
        new_parent = frozenset([new_parent])
        new_parents = old_parents.union(new_parent)
        self.set_parents(new_parents)
        
    def get_parents(self):
        return self._parents

    def set_colours(self, colours):
        if not colours:
            self._colours = set()
        elif isinstance(colours, str):
            self._colours = set()
        elif isinstance(colours, set):
            self._colours = colours
        else: 
            raise ValueError("Input to DAGNodeWrapper.set_colours() not recognised")

    def add_colour(self, colour):
        self._colours.add(colour)
