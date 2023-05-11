import unittest

from .context import referencesurfer
from referencesurfer import surf

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
                                     None]
        for c, back_to_start in zip(classes, is_back_to_start_expected): 
            self.assertTrue(issubclass(c, surf.SurfAction))
            self.assertEqual(c.is_back_to_start(), back_to_start)
        