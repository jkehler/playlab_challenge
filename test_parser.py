import unittest
import parser


class TestParserMethods(unittest.TestCase):

    def test_parse_log_file(self):
        with self.assertRaises(AssertionError):
            parser.parse_log_file('nofile')

        records = parser.parse_log_file('test.log')

        self.assertEqual(len(records), 30)

    def test_mean_response(self):
        records = parser.parse_log_file('test.log')
        self.assertEqual(parser.mean_response(records), 76.8)

    def test_mode_response(self):
        records = parser.parse_log_file('test.log')
        self.assertEqual(parser.mode_response(records), 18)

    def test_median_response(self):
        records = parser.parse_log_file('test.log')
        self.assertEqual(parser.median_response(records), 36.5)

    def test_mode_dyno(self):
        records = parser.parse_log_file('test.log')
        self.assertEqual(parser.mode_dyno(records), 'web.1')


if __name__ == '__main__':
    unittest.main()
