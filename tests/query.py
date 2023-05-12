#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	query.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-05-08
# Copyright: 	Alessandro Gerada, Nada Reza 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""External API query testers"""

import unittest

from .context import referencesurfer
from referencesurfer import paper_nodes

class CrossRefBadDOITestCase(unittest.TestCase): 
    def test_bad_query_result(self): 
        bad_doi = '12345'
        bad_query = referencesurfer.query_from_DOI(bad_doi)
        self.assertIsNone(bad_query)

class CrossRefGoodDOITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # using Howard et al ChatGPT paper 
        good_doi = '10.1016/S1473-3099(23)00113-5'
        cls.good_query = referencesurfer.query_from_DOI(good_doi)

    def test_query_instance(self):
        self.assertIsInstance(self.good_query, dict)
    
    def test_paper_maker_from_query_result(self):
        paper = referencesurfer.query_handlers.make_paper_from_query(self.good_query)
        self.assertIsInstance(paper, paper_nodes.Paper)
        
class DOICleanerTestCase(unittest.TestCase): 
    def test_clean_up_DOI(self): 
        doi_link = 'https://doi.org/10.1000/182' # valid DOI link to DOI handbook
        doi = '10.1000/182'
        same_doi = referencesurfer.query_handlers.clean_up_DOI(doi)
        self.assertEqual(doi, same_doi)

        link_removed = referencesurfer.query_handlers.clean_up_DOI(doi_link)
        self.assertEqual(doi, link_removed)

if __name__ == '__main__': 
    unittest.main()
