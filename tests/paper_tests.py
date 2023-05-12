#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	paper_tests.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-05-08
# Copyright: 	Alessandro Gerada, Nada Reza 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""Paper class testers"""

import unittest

from .context import referencesurfer

class PaperTestCase(unittest.TestCase): 
    def test_paper_name(self): 
        doi_link = 'https://doi.org/10.1000/182' # valid DOI link to DOI handbook
        doi = '10.1000/182'
        paper = referencesurfer.Paper(DOI=doi, 
                                      title='DOI Handbook', 
                                      author='doi_foundation', 
                                      year = '2019', 
                                      references=[{'DOI': '10.1016/S1473-3099(23)00113-5', 
                                                   'title': "ChatGPT and infection",
                                                   'author': 'howard', 
                                                   'year': '2023'}])
        self.assertIsInstance(paper, referencesurfer.paper_nodes.Paper)
        self.assertEqual(paper.get_DOI(), doi)
        howard_reference = paper.get_references()[0]
        self.assertIsInstance(howard_reference, referencesurfer.paper_nodes.Paper)

class ChangePaperDataTestCase(unittest.TestCase): 
    @classmethod
    def setUpClass(cls):
        cls.howard_paper = referencesurfer.paper_nodes.Paper(DOI='10.1016/S1473-3099(23)00113-5',
                                                             title = "ChatGPT and infection",
                                                             author='howard',
                                                             year='2023')
        
    def test_overwrite_data(self): 
        new_doi = '10.111/123'
        self.howard_paper.change_data({'doi': new_doi})
        self.assertEqual(new_doi, self.howard_paper.get_DOI())
        
        with self.assertRaises(KeyError):
            self.howard_paper.change_data({'new_data': 'x'})

if __name__ == '__main__': 
    unittest.main()
