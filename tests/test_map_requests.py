import unittest
from unittest.mock import ANY
from unittest.mock import patch

from geobeam import map_requests


class MapRequestsTest(unittest.TestCase):
  def setUp(self):
    point_one = (37.4178134, -122.086011)
    point_two = (37.4179142, -122.0858751)
    point_three = (37.4211366, -122.0936967)
    point_four = (37.4216022, -122.0964737)

    self.polyline = "idkcFp|chVSYW?Ai@kB@Y?ClAAjAQ?AV?BM@AH\\C`E@dFAvB?nFB@J|B@]zN_@`PAh@EzAwAL_AHqAHaEZuERgCRkAF@V[LW@q@BWESKKHGNOTWBwCBK?}ANUHGFEHOZMAATAz@EtBOjH"
    self.points = [point_one, point_two, point_three, point_four]
    self.distances = [16, 13, 266]

    self.sample_directions_response = [
      {
        'bounds': {}, 
        'copyrights': 'Map data ©2020', 
        'legs': [
          {
          'distance': {'text': '1.4 mi', 'value': 2307},
          'end_location': {'lat': 37.4216022, 'lng': -122.0964737},
          'start_location': {'lat': 37.4178134, 'lng': -122.086011},
          'steps': [
            {
              'distance': {'text': '52 ft', 'value': self.distances[0]},
              'end_location': {'lat': point_two[0], 'lng': point_two[1]},
              'polyline': {'points': 'idkcFp|chVSY'}, 
              'start_location': {'lat': point_one[0], 'lng': point_one[1]}
            },
            {
              'distance': {'text': '43 ft', 'value': self.distances[1]},
              'end_location': {'lat': point_three[0], 'lng': point_three[1]},
              'polyline': {'points': '}dkcFv{chVW?'},
              'start_location': {'lat': point_two[0], 'lng': point_two[1]}
            },
            {
              'distance': {'text': '0.2 mi', 'value': self.distances[2]},
              'end_location': {'lat': point_four[0], 'lng': point_four[1]},
              'polyline': {'points': 'cykcFrlehVUHCDC@CDABCDKTMAAT?JAn@Cz@Ax@AVGpCCnAAp@'},
              'start_location': {'lat': point_three[0], 'lng': point_three[1]}
            }
          ],
          'traffic_speed_entry': [],
          'via_waypoint': []
          }
        ],
        'overview_polyline': {'points': self.polyline},
        'summary': 'Rengstorff Ave'
      }
    ]

    self.elevations = [3.45, 3.67, 3.78, 3.89]
    self.sample_elevations_response = [
      {
         "elevation" : self.elevations[0],
         "location" : {
            "lat" : point_one[0],
            "lng" : point_one[1]
         },
         "resolution" : 4.771975994110107
      },
      {
         "elevation" : self.elevations[1],
         "location" : {
            "lat" : point_two[0],
            "lng" : point_two[1]
         },
         "resolution" : 4.771975994110107
      },
      {
         "elevation" : self.elevations[2],
         "location" : {
            "lat" : point_three[0],
            "lng" : point_three[1]
         },
         "resolution" : 4.771975994110107
      },
      {
         "elevation" : self.elevations[3],
         "location" : {
            "lat" : point_four[0],
            "lng" : point_four[1]
         },
         "resolution" : 4.771975994110107
      }

    ]

  @patch('geobeam.map_requests.datetime')
  @patch('geobeam.map_requests.GMAPS.directions')
  @patch('geobeam.map_requests.parse_directions_response')
  def test_request_directions(self, mock_parse_directions_response, mock_gmaps_directions, mock_datetime):
    mock_gmaps_directions.return_value = self.sample_directions_response
    mock_parse_directions_response.return_value = (self.points, self.distances, self.polyline)

    result = map_requests.request_directions(self.points[0], self.points[-1])

    mock_gmaps_directions.assert_called_once_with(self.points[0], self.points[-1], mode="walking", departure_time=ANY)
    mock_parse_directions_response.assert_called_once_with(self.sample_directions_response)
    self.assertEqual(result[0], self.points)
    self.assertEqual(result[1], self.distances)
    self.assertEqual(result[2], self.polyline)

  def test_parse_directions(self):
    result = map_requests.parse_directions_response(self.sample_directions_response)
    
    self.assertEqual(result[0], self.points)
    self.assertEqual(result[1], self.distances)
    self.assertEqual(result[2], self.polyline)

  def test_parse_directions_invalid_response(self):
    with self.assertRaises(ValueError):
      result = map_requests.parse_directions_response([])

  @patch('geobeam.map_requests.GMAPS.elevation')
  @patch('geobeam.map_requests.parse_elevations_response')
  def test_request_elevations(self, mock_parse_elevations_response, mock_gmaps_elevation):
    mock_gmaps_elevation.return_value = self.sample_elevations_response
    mock_parse_elevations_response.return_value = self.elevations

    result = map_requests.request_elevations(self.points)

    mock_gmaps_elevation.assert_called_once_with(self.points)
    mock_parse_elevations_response.assert_called_once_with(self.sample_elevations_response)
    self.assertEqual(result, self.elevations)

  def test_parse_elevations_response(self):
    result = map_requests.parse_elevations_response(self.sample_elevations_response)

    self.assertEqual(result, self.elevations)

if __name__ == '__main__':
  unittest.main()
