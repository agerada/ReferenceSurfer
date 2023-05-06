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