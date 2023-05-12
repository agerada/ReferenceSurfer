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

from .paper_nodes import Paper, DAGNodeWrapper

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

def make_paper_from_query(query, use_pubmed = False, parents = None, depth = None, score = None,
                          colours = None):
    message = query['message']
    doi = message['DOI']
    title = message['title']
    date_time = message['created']['date-time']
    year = datetime.fromisoformat(date_time).year
    references = message['reference'] if message['references-count'] > 0 else None
    author = message['author']

    paper = DAGNodeWrapper(DOI=doi,
                 title=title,
                 author=author,
                 year=year,
                 references=references,
                 parents = parents, 
                 depth = depth,
                 score = score, 
                 colours = colours)
    
    if not use_pubmed: 
        return paper

    return overwrite_with_pubmed_data(paper)

def overwrite_with_pubmed_data(paper): 
    """
    returns modified paper with overwritten pubmed data
    """
    doi = paper.get_DOI()
    pmiddoi = clean_up_DOI(doi)
    pmid = fetch.pmids_for_query(pmiddoi)
    pubmed_article = fetch.article_by_pmid(pmid)

    if not paper.get_title():
        try:
            paper.change_data({'title': pubmed_article.title})
        except:
            pass
    
    if not paper.get_author(): 
        try: 
            author = pubmed_article.authors[0]
            author = author.rpartition(" ")[0]
            paper.change_data({'author': author})
        except: 
            pass
    
    # year overwritten even if present since pubmed > crossref
    try:
        paper.change_data({'year': pubmed_article.year})
    except:
        pass

    return paper

def clean_up_DOI(doi): 
    return doi.rpartition('.org/')[-1] if '.org/' in doi else doi
