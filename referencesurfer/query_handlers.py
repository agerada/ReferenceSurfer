#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	query_handlers.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-05-06
# Copyright: 	Alessandro Gerada, Nada Reza 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""Handlers to interact with external APIs such as CrossRef and Pubmed"""

from habanero import Crossref
from datetime import datetime
from metapub import PubMedFetcher
import sys
import os

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from paper_nodes import Paper

cr = Crossref()
fetch = PubMedFetcher()

def query_from_DOI(doi: str): 
    try: 
        query = cr.works(doi)
    except: 
        print(f"Failed to pull DOI {doi}")
        return None
    
    if query['message-type'] == 'work': 
        print(f"Found paper: {doi}")
        return query
    
    print(f"Unable to pull {doi}")
    return None

def make_paper_from_query(query):
    message = query['message']
    doi = message['DOI']
    if '.org/' in doi:
        pmiddoi = doi.rpartition('.org/')[-1]
    else:
        pmiddoi = doi
    pmid = fetch.pmids_for_query(pmiddoi)
    article = fetch.article_by_pmid(pmid)
    title = message['title']
    if title == None:
        try:
            title = article.title
        except:
            pass
    author = message['author']
    if author == None:
        author = article.authors
        author = article.authors[0]
        author = author.rpartition(" ")[0]        
    date_time = message['created']['date-time']
    if article.year:
        year = article.year
    else: 
        year = datetime.fromisoformat(date_time).year
    references = message['reference'] if message['references-count'] > 0 else None
    return Paper(DOI=doi,
                 title=title,
                 author=author,
                 year=year,
                 references=references)
