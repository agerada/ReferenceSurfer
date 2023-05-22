#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: 	drawing_test.py
# Author: 	Alessandro Gerada, Nada Reza
# Date: 	2023-05-22
# Copyright: 	Alessandro Gerada 2023
# Email: 	alessandro.gerada@liverpool.ac.uk

"""Documentation"""

import unittest
from referencesurfer import surf
from tests.surfing_test import make_test_corpus
import matplotlib.pyplot as plt

class DrawingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_papers, cls.starting_corpus = make_test_corpus()
        cls.surfer = surf.Surfer(starting_papers=cls.starting_corpus)
        for _ in range(100):
            cls.surfer.iterate_surf()

    def test_draw_graph(self):
        try:
            self.surfer.draw_graph()
            plt.plot()
        except:
            self.fail("Surfer.draw_graph() failed with default args")
        
        try:
            self.surfer.draw_graph(labels=lambda x: x.get_DOI())
            plt.plot()
        except:
            self.fail("Surfer.draw_graph() failed with lambda arg for labels")

        try:
            mock_labels_list = [str(i) for i in range(len(self.all_papers))]
            self.surfer.draw_graph(labels=mock_labels_list)
            plt.plot()
        except:
            self.surfer.draw_graph("Surfer.draw_graph() failed with mock label sequence")

        try:
            mock_labels_list = [str(i) for i in range(len(self.all_papers))]
            mock_labels_dict = {node: label for node,label in zip(self.all_papers, mock_labels_list)}
            self.surfer.draw_graph(labels=mock_labels_dict)
            plt.plot()
        except:
            self.surfer.draw_graph("Surfer.draw_graph() failed with mock dict of labels")

        with self.assertRaises(ValueError):
            self.surfer.draw_graph(labels=[1,2,3])

        with self.assertRaises(ValueError):
            self.surfer.draw_graph(labels={self.all_papers[0]: "test"})
            
if __name__ == '__main__':
    unittest.main()
