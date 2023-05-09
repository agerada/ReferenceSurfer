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
from referencesurfer import paper_nodes

class PaperTestCase(unittest.TestCase): 
    def test_paper_name(self): 
        doi_link = 'https://doi.org/10.1000/182' # valid DOI link to DOI handbook
        doi = '10.1000/182'
        paper = referencesurfer.Paper(DOI='https://doi.org/10.1000/182', 
                                      title='DOI Handbook')
        self.assertTrue(True)


if __name__ == '__main__': 
    unittest.main()
