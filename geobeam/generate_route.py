# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate route that can be made into User Motion File based on two locations.

Classes for Location, Route, and TimedRoute. A Route is a list of points that
connect a user given start and end location. TimedRoute is a child class of
Route and incorporates a user specified speed of travel and point frequency,
which can be used to create a user motion file (10 Hz) with various simulated
speeds (walking, running, biking)

  Typical usage example:
  user_motion = TimedRoute.from_start_and_end(location1, location2, TRANSPORT_SPEEDS["walking"], TEN_HZ)
  user_motion = TimedRoute.from_gpx(/path/to/gpx/file, TRANSPORT_SPEEDS["walking"], TEN_HZ)
  user_motion.write_route("userwalking.csv")
"""

import csv
import os

from geobeam.gps_utils import calculate_distance
from geobeam.gps_utils import Location
from geobeam.gpx_parser import GpxFileParser
from geobeam.map_requests import request_directions
from geobeam.map_requests import request_elevations

FILE_FOLDER_PATH = "geobeam/user_motion_files/"


class Route():
  """An object for a route based on the input of a start and ending location.

  Attributes:
    route: a list of Location objects for each point on the route
    distances: a list of distances between each pair of consecutive
    locations in meters
  """

  def __init__(self, route, distances):
    self.route = route
    self.distances = distances

  @classmethod
  def from_start_and_end(cls, start_location, end_location):
    """Creates route from start and end and initializes Route object.

    Args:
      start_location: a Location object for the start of the route
      end_location: a Location object for the end of the route

    Returns:
      initialized Route object
    """
    route, distances = cls._generate_route_from_start_and_end(start_location,
                                                              end_location)
    return cls(route, distances)

  @classmethod
  def from_gpx(cls, gpx_source_path):
    """Creates route from GPX file and initializes Route object.

    Args:
      gpx_source_path: path to gpx file to parse for route

    Returns:
      initialized Route object
    """
    route, distances = cls._generate_route_from_gpx(gpx_source_path)
    return cls(route, distances)

  def _generate_route_from_start_and_end(start_location, end_location):
    """Create a route by requesting from Maps API and then adding altitudes/xyz.

    sets attributes for the class based on API response and then calls
    add_altitudes() to request elevation data for each point, and then add xyz
    conversion to each point

    Args:
      start_location: a Location object for the start of the route
      end_location: a Location object for the end of the route

    Returns:
      list of Location objects in order of the points on the route
      a list of distances between those points (in meters)
    """
    route = []
    locations, distances = request_directions(start_location.get_lat_lon_tuple(),
                                              end_location.get_lat_lon_tuple())
    elevations = request_elevations(locations)
    for location, altitude in zip(locations, elevations):
      latitude = location[0]
      longitude = location[1]
      route.append(Location(latitude, longitude, altitude))
    return (route, distances)

  def _generate_route_from_gpx(gpx_source_path):
    """Create a route by parsing track points from GPX File.

    Args:
      gpx_source_path: file path for GPX file to be parsed and used for route

    Returns:
      list of Location objects in order of the points on the route
      a list of distances between those points (in meters)
    """
    route = []
    distances = []
    gpx_file_parser = GpxFileParser()
    locations = gpx_file_parser.parse_file(gpx_source_path)
    previous_location = None

    for location in locations:
      route.append(Location(*location))
      if previous_location:
        distances.append(calculate_distance(previous_location, location))
      previous_location = location

    return (route, distances)

  def write_route(self, file_name):
    """Write route into csv with each line as x,y,z.

    Args:
      file_name: name of file to write route to
    """
    write_array = [location.get_xyz_tuple() for location in self.route]
    _write_to_csv(FILE_FOLDER_PATH+file_name, write_array)


class TimedRoute(Route):
  """An object for a route that has a desired speed and point frequency.

  Attributes:
    speed: how fast the person moves through the route in meters/second
    frequency: how many points per second the timed route should have (Hz)
    route: a list of Location objects for each point on the route
    distances: a list of distances for each pair of consecutive locations
    in meters
  """

  def __init__(self, route, distances, speed, frequency):
    self.speed = speed
    self.frequency = frequency
    Route.__init__(self, route, distances)

  @classmethod
  def from_start_and_end(cls, start_location, end_location, speed, frequency):
    """Creates route from start and end and initializes TimedRoute object.

    Args:
      start_location: a Location object for the start of the route
      end_location: a Location object for the end of the route
      speed: float, speed of route in meters/second
      frequency: float, points per second for timed route (Hz)

    Returns:
      initialized and upsampled TimedRoute object
    """
    route, distances = cls._generate_route_from_start_and_end(start_location,
                                                              end_location)
    timed_route = cls(route, distances, speed, frequency)
    timed_route.upsample_route()
    return timed_route

  @classmethod
  def from_gpx(cls, gpx_source_path, speed, frequency):
    """Creates route from GPX file and initializes TimedRoute object.

    Args:
      gpx_source_path: path to gpx file to parse for route
      speed: float, speed of route in meters/second
      frequency: float, points per second for timed route (Hz)

    Returns:
      initialized and upsampled TimedRoute object
    """
    route, distances = cls._generate_route_from_gpx(gpx_source_path)
    timed_route = cls(route, distances, speed, frequency)
    timed_route.upsample_route()
    return timed_route

  def upsample_route(self):
    """Upsample the TimedRoute to match the desired speed and frequency.

    for each consecutive set of points, the change in lat,lon,alt is divided
    by split amongst the number of new points that need to be created so
    that there is roughly an equal distance (1/points_per_meter) between
    each of the points in the upsampled route.
    """
    points_per_meter = self.frequency/self.speed
    new_route = []

    # TODO(ameles) check if we need to do this for better location fixing
    # fill first 10 cycles with starting location
    for i in range(10):
      new_route.append(self.route[0])

    for i in range(len(self.distances)):
      distance = self.distances[i]
      start_point = self.route[i]
      end_point = self.route[i+1]
      new_route.append(start_point)

      points_needed = int(distance*points_per_meter)-1
      if points_needed > 0:
        latitude_delta = (end_point.latitude-start_point.latitude) / points_needed
        longitude_delta = (end_point.longitude-start_point.longitude) / points_needed
        altitude_delta = (end_point.altitude-start_point.altitude) / points_needed
        for j in range(1, points_needed):
          new_point = Location(start_point.latitude + latitude_delta*j,
                               start_point.longitude + longitude_delta*j,
                               start_point.altitude + altitude_delta*j)
          new_route.append(new_point)
    new_route.append(self.route[-1])
    self.route = new_route
    self.distances = [1/points_per_meter for x in range(len(new_route)-1)]

  def write_route(self, file_name):
    """write route into csv with each line as time,x,y,z.

    time starts at 0.0 seconds and time values are rounded to one decimal place

    Args:
      file_name: name of file to write route to
    """
    write_array = []
    time = 0.0
    for location in self.route:
      write_array.append(("%.1f" % (time,),)+location.get_xyz_tuple())
      time = time + (1/self.frequency)
    _write_to_csv(FILE_FOLDER_PATH+file_name, write_array)


def _write_to_csv(file_name, value_array):
  if not os.path.exists(FILE_FOLDER_PATH):
    os.makedirs(FILE_FOLDER_PATH)
  with open(file_name, "w") as csv_file:
    csv.writer(csv_file).writerows(value_array)
