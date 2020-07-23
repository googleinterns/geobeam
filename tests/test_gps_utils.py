import unittest
from unittest.mock import patch

from geobeam import gps_utils


class LocationTest(unittest.TestCase):
  def setUp(self):
    self.geodetic_one = (37.4178134, -122.086011, 3.45)
    self.ecef_one = (-2694180.667, -4297222.330, 3854325.576)
    self.geodetic_two = (37.4211366, -122.0936967, -10.0)
    self.ecef_two = (-2694174.993, -4297213.279, 3854317.404)
    self.geodetic_three = (31.230441, 121.467685, 4.50)
    self.ecef_three = (-2849585.509, 4655993.331, 3287769.376)

  @patch('geobeam.gps_utils.geodetic_to_cartesian')
  def test_location_init(self, mock_geodetic_to_cartesian):
    geodetic_coordinate = (37.4178134, -122.086011, 3.45)
    ecef_coordinate = (-2694180.667, -4297222.330, 3854325.576)
    mock_geodetic_to_cartesian.return_value = ecef_coordinate
    lat, lon, alt = geodetic_coordinate

    location = gps_utils.Location(lat, lon, alt)

    self.assertEqual(location.x, ecef_coordinate[0])
    self.assertEqual(location.y, ecef_coordinate[1])
    self.assertEqual(location.z, ecef_coordinate[2])
    self.assertEqual(location.latitude, lat)
    self.assertEqual(location.longitude, lon)
    self.assertEqual(location.altitude, alt)

  @patch('geobeam.gps_utils.geodetic_to_cartesian')
  def test_location_init_no_altitude(self, mock_geodetic_to_cartesian):
    geodetic_coordinate = (37.4178134, -122.086011)
    ecef_coordinate = (-2694180.667, -4297222.330, 3854325.576)
    mock_geodetic_to_cartesian.return_value = ecef_coordinate
    lat, lon = geodetic_coordinate

    location = gps_utils.Location(lat, lon)
    
    self.assertEqual(location.x, ecef_coordinate[0])
    self.assertEqual(location.y, ecef_coordinate[1])
    self.assertEqual(location.z, ecef_coordinate[2])
    self.assertEqual(location.latitude, lat)
    self.assertEqual(location.longitude, lon)
    self.assertEqual(location.altitude, 0)

class CoordinateConversionTest(unittest.TestCase):

  def coordinate_assertions(self, geodetic_coordinate, ecef_coordinate):
    lat, lon, alt = geodetic_coordinate
    x, y, z = ecef_coordinate

    result = gps_utils.geodetic_to_cartesian(lat, lon, alt)

    self.assertAlmostEqual(result[0], x, places=3)
    self.assertAlmostEqual(result[1], y, places=3)
    self.assertAlmostEqual(result[2], z, places=3)

    back_conversion = gps_utils.cartesian_to_geodetic(result[0], result[1], result[2])

    self.assertAlmostEqual(back_conversion[0], lat, places=5)
    self.assertAlmostEqual(back_conversion[1], lon, places=5)
    self.assertAlmostEqual(back_conversion[2], alt, places=3)

    result = gps_utils.cartesian_to_geodetic(x, y, z)

    self.assertAlmostEqual(result[0], lat, places=5)
    self.assertAlmostEqual(result[1], lon, places=5)
    self.assertAlmostEqual(result[2], alt, places=3)

  def test_geodetic_to_cartesian_mountainview(self):
    geodetic_mountainview = (37.4178134, -122.086011, 3.45)
    ecef_mountainview = (-2694180.667, -4297222.330, 3854325.576)

    self.coordinate_assertions(geodetic_mountainview, ecef_mountainview)

  def test_geodetic_to_cartesian_mountainview_negative_altitude(self):
    geodetic_mountainview_negative_altitude = (37.4211366, -122.0936967, -10.000)
    ecef_mountainview_negative_altitude = (-2694632.326, -4296661.975, 3854610.329)

    self.coordinate_assertions(geodetic_mountainview_negative_altitude, ecef_mountainview_negative_altitude)

  def test_geodetic_to_cartesian_shanghai(self):
    geodetic_shanghai = (31.230441, 121.467685, 4.5)
    ecef_shanghai = (-2849585.509, 4655993.331, 3287769.376)

    self.coordinate_assertions(geodetic_shanghai, ecef_shanghai)

if __name__ == '__main__':
    unittest.main()
