import unittest
from krux.regex import simple_pattern_to_regex


class TestSimplePattern(unittest.TestCase):
    def test_basic_usage(self):
        self.assertEqual(
            r'abc/(?P<def>.*)/(?P<gh>.*)\.nc',
            simple_pattern_to_regex('abc/{def}/{gh:+02d}.nc')
        )

    def test_path(self):
        self.assertEqual(
            r'abc/(?P<DEF>.*)/(?P<gh>[^/]*)\.nc',
            simple_pattern_to_regex('abc/{DEF}/{gh:+02d}.nc', mode='path')
        )

    def test_keep_dots(self):
        def test_basic_usage(self):
            self.assertEqual(
                r'abc/(?P<def>.*)/(?P<gh>.*).nc',
                simple_pattern_to_regex('abc/{def}/{gh:+02d}.nc', keep_dots=True)
            )

    def test_strict(self):
        self.assertEqual(
            r'^abc/(?P<def>.*)/(?P<gh>.*)\.nc$',
            simple_pattern_to_regex('abc/{def}/{gh:+02d}.nc', strict=True)
        )

    def test_sep_chars(self):
        self.assertEqual(
            r'abc/(?P<def>[^/?#]*)/(?P<gh>[^/?#]*)\.nc',
            simple_pattern_to_regex('abc/{def}/{gh:+02d}.nc', sep_chars='/?#')
        )

    def test_raw_regex(self):
        r = r'\d+/(?P<name>\w+)'
        self.assertEqual(
            r,
            simple_pattern_to_regex(r)
        )

    @unittest.expectedFailure
    def test_invalid(self):
        simple_pattern_to_regex('{abc}/{{de}')


if __name__ == '__main__':
    unittest.main()
