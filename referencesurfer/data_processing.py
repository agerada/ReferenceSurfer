#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	data_processing.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-05-06
# Copyright: 	Alessandro Gerada, Nada Reza 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""Helper functions mainly for Input/Output"""

from unidecode import unidecode
import csv
from .paper_nodes import DAGNodeWrapper

def read_keywords(path: str) -> list[tuple]: 
    keywords = []
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            keyterm = row['keyterms']
            value = row['value']
            keyword = (unidecode(keyterm).lower(), value)
            keywords.append(keyword)
    return keywords

def read_imported_authors(path: str) -> list:
    important_authors = []
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            author = row['Last']
            author = unidecode(author)
            author = author.lower()
            important_authors.append(author)
    return important_authors

def read_starting_corpus(path: str) -> set: 
    _starting_DOIs = set()
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            doi = row['DOI']
            if doi: 
                _starting_DOIs.add(doi)
    return _starting_DOIs

def read_keyword_colours(path: str) -> dict:
    """
    Read keyword colours from .csv
    Returns dictionary of keyword: colour
    """
    _keyword_colours = dict()
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            keyword = row['keyword']
            _keyword_colours[keyword] = row['colour']
            
    return _keyword_colours

def write_output(path: str, results: list[DAGNodeWrapper]) -> None: 
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(['DOI', 'author', 'title', 'score', 'times_seen'])
        for node in results:
            writer.writerow([node.get_DOI(), 
                                node.get_title(), 
                                node.get_first_author(),
                                node.score, 
                                node.counter])
