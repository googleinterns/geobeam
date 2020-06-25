#!/usr/bin/env python3

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

"""Generate a route that can be made into a User Motion File based on two locations.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""

import sys
from datetime import datetime

import googlemaps
import pprint

from map_requests import request_directions,request_elevations

#average in meters per second
WALKING_SPEED = 1.4

class Location(object):
  """An object for a location (in the form of a set of coordinates)

  Attributes:
      latitude: A float for the latitude of the location in Decimal Degrees
      longitude A float for the longitude of the location in Decimal Degrees
  """

  def __init__(self,latitude,longitude):
    self.latitude = latitude
    self.longitude = longitude
    self.altitude = None
    self.x = None
    self.y = None
    self.z = None

  def get_lat_lon_tuple(self):
    return (self.latitude,self.longitude)

  def get_XYZ(Self):
    pass

  def __repr__(self):
    return 'Location(%s, %s, %s)' % (self.latitude, self.longitude, self.altitude)

class Route(object):
  """An object for a route based on the input of a start and ending location

  Attributes:
      start_location: a Location object for the start of the route
      end_location: a Location object for the end of the route
      route: a list of Location objects for each point on the route
  """

  def __init__(self, start_location, end_location):
    self.start_location = start_location
    self.end_location = end_location
    self.route = []
    self.distances = []
    self.durations = []
    self.polyline = None

  def create_route(self):
    locations,self.distances,self.durations,self.polyline = request_directions(self.start_location.get_lat_lon_tuple(),self.end_location.get_lat_lon_tuple())
    route = []
    for location in locations:
      latitude = location[0]
      longitude = location[1]
      route.append(Location(latitude,longitude))
    self.route = route
  
  def add_altitudes(self):
    locations = []
    for location in self.route:
      locations.append(location.get_lat_lon_tuple())
    elevations = request_elevations(locations)
    for location,elevation in zip(self.route,elevations):
      location.altitude = elevation
  
  def upsample_route(self):
    pass

  def write_route(self,file_name):
    pass


def main():
  #add typechecking for input
  location1 = Location(37.417747,-122.086086)
  location2 = Location(37.421624, -122.096472)
  route = Route(location1,location2)
  route.create_route()
  route.add_altitudes()
  print(route.route)
if __name__ == '__main__':
	sys.exit(main())
