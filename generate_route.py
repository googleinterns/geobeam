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
  user_motion = TimedRoute(location1,location2,TRANSPORT_SPEEDS["walking"],10)
  user_motion.create_route()
  user_motion.write_route("usermotiontestfile.csv")
"""

import csv

from gps_utils import Location
from map_requests import request_directions
from map_requests import request_elevations


class Route():
  """An object for a route based on the input of a start and ending location.

  Attributes:
    start_location: a Location object for the start of the route
    end_location: a Location object for the end of the route
    route: a list of Location objects for each point on the route
    distances: a list of distances between each pair of consecutive
    locations in meters
    polyline: an encoded format for the route given by the Maps API
    for ease of drawing
  """

  def __init__(self, start_location, end_location):
    self.start_location = start_location
    self.end_location = end_location
    self.route = []
    self.distances = []
    self.polyline = None
    self.create_route()

  def create_route(self):
    """Create a route by requesting from Maps API and then adding altitudes/xyz to each point.

    sets attributes for the class based on API response and then calls
    add_altitudes() to request elevation data for each point, and then add xyz
    conversion to each point
    """
    route = []
    locations, self.distances, self.polyline = request_directions(self.start_location.get_lat_lon_tuple(), self.end_location.get_lat_lon_tuple())
    elevations = request_elevations(locations)
    for location, altitude in zip(locations, elevations):
      latitude = location[0]
      longitude = location[1]
      route.append(Location(latitude, longitude, altitude))
    self.route = route
    self.start_location = route[0]
    self.end_location = route[-1]

  def write_route(self, file_name):
    """Write route into csv with each line as x,y,z.

    Args:
      file_name: name of file to write route to
    """
    write_array = [location.get_xyz_tuple() for location in self.route]
    _write_to_csv(file_name, write_array)


class TimedRoute(Route):
  """An object for a route that has a desired speed and point frequency.

  Attributes:
    start_location: a Location object for the start of the route
    end_location: a Location object for the end of the route
    speed: how fast the person moves through the route in meters/second
    frequency: how many points per second the timed route should have (Hz)
    route: a list of Location objects for each point on the route
    distances: a list of distances for each pair of consecutive locations
    in meters
    polyline: an encoded format for the route given by the Maps API
    for ease of drawing
  """

  def __init__(self, start_location, end_location, speed, frequency):
    self.speed = speed
    self.frequency = frequency
    Route.__init__(self, start_location, end_location)

  def create_route(self):
    Route.create_route(self)
    self.upsample_route()

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
    _write_to_csv(file_name, write_array)


def _write_to_csv(file_name, value_array):
  with open(file_name, "w") as csv_file:
    csv.writer(csv_file).writerows(value_array)
