import unittest

from geobeam import gpx_parser

class GpxFileParserTest(unittest.TestCase):

  def setUp(self):
    self.fileparser = gpx_parser.GpxFileParser()

  def test_get_file_type_valid(self):
    xml_file_type = self.fileparser._get_file_type('testfile2.xml')

    self.assertEqual(".xml", xml_file_type)

  def test_get_file_type_none(self):
    none_file_type = self.fileparser._get_file_type(None)

    self.assertIsNone(none_file_type)

  def test_parse_gpx_success(self):
    expected_points = [(63.17964, -174.12954, 4.91),
                       (63.17965, -174.12955, 4.91)]
                       
    result = self.fileparser.parse_file('tests/test_gpx_file.gpx')

    self.assertEqual(expected_points, result)

  def test_parse_gpx_no_altitude(self):
    expected_points = [(63.17964, -174.12954, 0),
                       (63.17965, -174.12955, 0)]

    result = self.fileparser.parse_file('tests/test_gpx_file_no_alt.gpx')

    self.assertEqual(expected_points, result)

  def test_parse_gpx_no_trkpts_return_none(self):
    result = self.fileparser.parse_file('tests/test_gpx_file_no_trkpts.gpx')

    self.assertIsNone(result)

  def test_parse_gpx_invalid_file_return_none(self):
    result = self.fileparser.parse_file('invalid_filename.csv')

    self.assertIsNone(result)

if __name__ == "__main__":
  unittest.main()
