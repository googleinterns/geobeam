import unittest
from unittest.mock import mock_open
from unittest.mock import patch

import geobeam


class RouteTest(unittest.TestCase):

  def setUp(self):
    self.location1 = (26.10000, 86.10299)
    self.location2 = (26.105345, 86.10344)
    self.location3 = (26.23334, 86.23432)
    self.altitudes = [5.11, 4.3, 7.4]
    self.distances = [5, 10]
    self.polyline = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"

  @patch('geobeam.generate_route.Location.get_xyz_tuple')
  @patch('geobeam.generate_route.request_elevations')
  @patch('geobeam.generate_route.request_directions')
  def test_create_route(self, mock_directions_request, mock_elevations_request, mock_get_xyz_tuple):
    start_location = geobeam.gps_utils.Location(*self.location1)
    end_location = geobeam.gps_utils.Location(*self.location3)
    test_points = [(self.location1[0], self.location1[1], self.altitudes[0]),
                   (self.location2[0], self.location2[1], self.altitudes[1]),
                   (self.location3[0], self.location3[1], self.altitudes[2])]
    location_list = [self.location1, self.location2, self.location3]
    mock_directions_request.return_value = (location_list, self.distances, self.polyline)
    mock_elevations_request.return_value = self.altitudes

    route = geobeam.generate_route.Route(start_location, end_location)

    mock_directions_request.assert_called_once_with(self.location1, self.location3)
    mock_elevations_request.assert_called_once_with(location_list)
    for point, test_point in zip(route.route, test_points):
      self.assertEqual((point.latitude, point.longitude, point.altitude), test_point)
    self.assertEqual(len(route.route), 3)
    self.assertEqual(route.distances, self.distances)
    self.assertEqual(route.polyline, self.polyline)

  @patch('geobeam.generate_route._write_to_csv')
  @patch('geobeam.generate_route.Location.get_xyz_tuple')
  @patch('geobeam.generate_route.Route.create_route')
  def test_write_route(self, mock_create_route, mock_get_xyz_tuple, mock_write_to_csv):
    start_location = geobeam.gps_utils.Location(*self.location1)
    end_location = geobeam.gps_utils.Location(*self.location3)
    filename = "writeroutetest.csv"
    test_xyz = [(-2849585.509, 4655993.331, 3287769.376),
                (-2694180.667, -4297222.330, 3854325.576),
                (1694180.667, -3297222.330, 2854325.576)]
    test_route = geobeam.generate_route.Route(start_location, end_location)
    mock_get_xyz_tuple.side_effect = test_xyz
    test_route.route = [geobeam.gps_utils.Location(*self.location1),
                        geobeam.gps_utils.Location(*self.location2),
                        geobeam.gps_utils.Location(*self.location3)]

    test_route.write_route(filename)

    mock_write_to_csv.assert_called_once_with("geobeam/user_motion_files/writeroutetest.csv", test_xyz)

class TimedRouteTest(unittest.TestCase):

  def setUp(self):
    self.location1 = (26.10000, 86.10299)
    self.location2 = (26.105345, 86.10344)
    self.location3 = (26.23334, 86.23432)
    self.altitudes = [5.11, 4.3, 7.4]
    self.distances = [5, 10]
    self.polyline = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
    self.location_list = [self.location1, self.location2, self.location3]

    self.test_points = [(self.location1[0], self.location1[1], self.altitudes[0]),
                        (self.location2[0], self.location2[1], self.altitudes[1]),
                        (self.location3[0], self.location3[1], self.altitudes[2])]

    self.patcher = patch('geobeam.generate_route.Location.get_xyz_tuple')
    self.mock_get_xyz_tuple = self.patcher.start()
    self.start_location = geobeam.gps_utils.Location(*self.location1)
    self.end_location = geobeam.gps_utils.Location(*self.location3)

  def tearDown(self):
    self.patcher.stop()

  @patch('geobeam.generate_route.TimedRoute.upsample_route')
  @patch('geobeam.generate_route.request_elevations')
  @patch('geobeam.generate_route.request_directions')
  def test_create_route_initializes_correctly(self, mock_directions_request, mock_elevations_request, mock_upsample_route):
    speed = 7  # meters per second
    frequency = 10  # Hz
    mock_directions_request.return_value = (self.location_list, self.distances, self.polyline)
    mock_elevations_request.return_value = self.altitudes

    route = geobeam.generate_route.TimedRoute(self.start_location, self.end_location, speed, frequency)

    mock_directions_request.assert_called_once_with(self.location1, self.location3)
    mock_elevations_request.assert_called_once_with(self.location_list)
    mock_upsample_route.assert_called_once()
    self.assertEqual(len(route.route), 3)
    for point, test_point in zip(route.route, self.test_points):
      self.assertEqual((point.latitude, point.longitude, point.altitude), test_point)

  @patch('geobeam.generate_route.request_elevations')
  @patch('geobeam.generate_route.request_directions')
  def test_upsample_route_correct_point_amount(self, mock_directions_request, mock_elevations_request):
    speed = 10  # meters per second
    frequency = 10  # Hz
    mock_directions_request.return_value = (self.location_list, self.distances, self.polyline)
    mock_elevations_request.return_value = self.altitudes
    test_point_count = sum([int(distance*frequency/speed)-1 for distance in self.distances]) + 11
    test_upsampled_distances = [speed/frequency for x in range(test_point_count-1)]

    route = geobeam.generate_route.TimedRoute(self.start_location, self.end_location, speed, frequency)

    # number of new points and original start points plus extra ten cycles of first point and last end point
    self.assertEqual(len(route.route), test_point_count)
    self.assertEqual(route.distances, test_upsampled_distances)

  @patch('geobeam.generate_route.request_elevations')
  @patch('geobeam.generate_route.request_directions')
  def test_upsample_route_no_downsample(self, mock_directions_request, mock_elevations_request):
    speed = 10  # meters per second
    frequency = 1  # Hz
    mock_directions_request.return_value = (self.location_list, self.distances, self.polyline)
    mock_elevations_request.return_value = self.altitudes
    test_point_count = 13  # 10 extra cycles of first point plus 3 original points

    route = geobeam.generate_route.TimedRoute(self.start_location, self.end_location, speed, frequency)

    self.assertEqual(len(route.route), test_point_count)

  @patch('geobeam.generate_route._write_to_csv')
  @patch('geobeam.generate_route.TimedRoute.create_route')
  def test_write_route(self, mock_create_route, mock_write_to_csv):
    filename = "writeroutetest.csv"
    speed = 10  # meters per second
    frequency = 10  # Hz
    test_xyz = [(-2849585.509, 4655993.331, 3287769.376),
                (-2694180.667, -4297222.330, 3854325.576),
                (1694180.667, -3297222.330, 2854325.576)]
    self.mock_get_xyz_tuple.side_effect = test_xyz
    expected_write_array = [('0.0', -2849585.509, 4655993.331, 3287769.376),
                            ('0.1', -2694180.667, -4297222.330, 3854325.576),
                            ('0.2', 1694180.667, -3297222.330, 2854325.576)]
    test_route = geobeam.generate_route.TimedRoute(self.start_location, self.end_location, speed, frequency)
    test_route.route = [geobeam.gps_utils.Location(*self.location1),
                        geobeam.gps_utils.Location(*self.location2),
                        geobeam.gps_utils.Location(*self.location3)]

    test_route.write_route(filename)

    mock_write_to_csv.assert_called_once_with("geobeam/user_motion_files/writeroutetest.csv", expected_write_array)


class CSVWriterTest(unittest.TestCase):

  @patch('geobeam.generate_route.csv')
  def test_write_to_csv(self, mock_csv):
    open_mock = mock_open()
    expected_write_array = [('0.0', -2849585.509, 4655993.331, 3287769.376),
                            ('0.1', -2694180.667, -4297222.330, 3854325.576),
                            ('0.2', 1694180.667, -3297222.330, 2854325.576)]

    with patch("geobeam.generate_route.open", open_mock, create=True):
      geobeam.generate_route._write_to_csv("geobeam/user_motion_files/test.csv", expected_write_array)

    open_mock.assert_called_with("geobeam/user_motion_files/test.csv", "w")
    mock_csv.writer.assert_called_once()
    mock_csv.writer().writerows.assert_called_once_with(expected_write_array)

if __name__ == '__main__':
  unittest.main()
