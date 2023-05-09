import unittest

from .context import referencesurfer

class SurfActionsTestCase(unittest.TestCase):
    def test_base_surf_action_class(self):
        x = referencesurfer.SurfAction
        print(x)
        self.assertEqual(type(x), type(referencesurfer.SurfAction))
