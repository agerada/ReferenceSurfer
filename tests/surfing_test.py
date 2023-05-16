import unittest

#from .context import referencesurfer
from referencesurfer import surf
from random import choice
from referencesurfer.paper_nodes import DAGNodeWrapper

class SurfActionsTestCase(unittest.TestCase):
    def test_base_surf_action_class(self):
        x = surf.SurfAction
        print(x)
        self.assertEqual(type(x), type(surf.SurfAction))

    def test_inherited_surf_action_classes(self): 
        classes = [surf.BackToStart, 
                   surf.InvalidReferences, 
                   surf.NewPaper, 
                   surf.PreviouslySeenPaper, 
                   surf.LowScorePaper, 
                   surf.StartingPaper]
        is_back_to_start_expected = [True, 
                                     False, 
                                     False, 
                                     False, 
                                     False, 
                                     True]
        for c, back_to_start in zip(classes, is_back_to_start_expected): 
            self.assertTrue(issubclass(c, surf.SurfAction))
            self.assertEqual(c.is_back_to_start(), back_to_start)
        
class SurferMainTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Simple structure: 
        0 ---> 1
            -> 2
            -> 3
        4 ---> 1 ---> 5
        6 ---> Nil

        """
        authors = ["Smith A", "England B", "Writer C"]
        #paper_0 = DAGNodeWrapper('0', 'paper_0', choice(authors), 2023)
        paper_1 = DAGNodeWrapper('0', 'paper_0', choice(authors), 2023)
        paper_2 = DAGNodeWrapper('1', 'paper_1', choice(authors), 2023)
        paper_3 = DAGNodeWrapper('2', 'paper_2', choice(authors), 2023)
        paper_4 = DAGNodeWrapper('3', 'paper_3', choice(authors), 2023)
        paper_5 = DAGNodeWrapper('4', 'paper_4', choice(authors), 2023)
        paper_6 = DAGNodeWrapper('5', 'paper_5', choice(authors), 2023)
        paper_7 = DAGNodeWrapper('6', 'paper_6', choice(authors), 2023)

        # set up reference links
        paper_1.set_references([paper_2, paper_3, paper_4])
        paper_5.set_references([paper_2])
        paper_2.set_references([paper_6])
        
        cls.all_papers = [paper_1, paper_2, paper_3, paper_4, paper_5, paper_6, paper_7]
        cls.starting_corpus = [paper_1, paper_5, paper_7]

    def test_create_surfer(self):
        # Step 1 - Test init of Surfer class
        surfer = surf.Surfer(starting_papers=self.starting_corpus)
        self.assertIsInstance(surfer, surf.Surfer)

        # Step 2 - Run 100 iterations without exception
        for _ in range(100): 
            surfer.iterate_surf()

        # Step 3 - Check that output graph structure is sensible 
        # Ensure papers have same parents as above schema
        # Indexed so that numbers match
        papers_post_surfing = list(surfer.graph.nodes)
        papers_post_surfing.sort(key = lambda x: x.get_DOI())
        self.assertEqual(papers_post_surfing[0].get_parents(), frozenset())
        self.assertEqual(papers_post_surfing[1].get_parents(), frozenset([papers_post_surfing[0], 
                                                                      papers_post_surfing[4]]))
        self.assertEqual(papers_post_surfing[2].get_parents(), frozenset([papers_post_surfing[0]]))
        self.assertEqual(papers_post_surfing[3].get_parents(), frozenset([papers_post_surfing[0]]))
        self.assertEqual(papers_post_surfing[4].get_parents(), frozenset())
        self.assertEqual(papers_post_surfing[5].get_parents(), frozenset([papers_post_surfing[1]]))
        self.assertEqual(papers_post_surfing[6].get_parents(), frozenset())

if __name__ == '__main__':
    unittest.main()
