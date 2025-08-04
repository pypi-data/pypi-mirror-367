import unittest
from krux.values import *
import json
import numpy as np


class TestValues(unittest.TestCase):
    def test_none_min_max(self):
        self.assertEqual(none_min(1, 2), 1)
        self.assertEqual(none_min(1, None), 1)
        self.assertEqual(none_min(None, 2), 2)
        self.assertEqual(none_min(None, None), None)

        self.assertEqual(none_max(1, 2), 2)
        self.assertEqual(none_max(1, None), 1)
        self.assertEqual(none_max(None, 2), 2)
        self.assertEqual(none_max(None, None), None)

    def test_json_safe(self):
        d = {"a": np.nan, "b": np.inf, "c": [1, np.nan], "d": {"e": 1, "f": np.inf, "g": np.array([np.nan, 2, np.inf])}, "s": "abc"}
        s = json_safe(d)
        print(s)
        j = json.dumps(s)
        print(j)


if __name__ == '__main__':
    unittest.main()
