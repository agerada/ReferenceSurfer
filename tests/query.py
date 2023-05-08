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
        paper = referencesurfer.make_paper_from_query(self.good_query)
        self.assertIsInstance(paper, referencesurfer.Paper)
        