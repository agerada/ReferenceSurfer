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

def read_antibiotic_colours(path: str) -> tuple[list, dict, dict]:
    """
    Read antibiotic colours form path .csv
    Return tuple of abx_list, abx_colours, abx_classes
    """
    _abx_list = []
    _abx_colours = dict()
    _abx_classes = dict()
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            abx = row['abx']
            colour = row['colour']
            abxclass = row['class']
            _abx_colours[abx] = colour
            _abx_classes[abx] = abxclass
            _abx_list.append(abx)
    return _abx_list, _abx_colours, _abx_classes