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

import googlemaps
from datetime import datetime
import pprint
from config import api_key
import sys

API_KEY = api_key

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

  def toTuple(self):
    return (self.latitude,self.longitude)

  def __repr__(self):
    return 'Location(%s, %s)' % (self.latitude, self.longitude)

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
    self.polyline = None

  def create_route(self):
    directions_response = request_directions(self.start_location,self.end_location)
    self.route,self.distances,self.polyline = parse_directions_response(directions_response)

  def upsample_route(self):
    pass

  def write_route(self,file_name):
    pass


def request_directions(start_location,end_location):
  gmaps = googlemaps.Client(key=API_KEY)  
  now = datetime.now()
  directions_response= gmaps.directions(start_location.toTuple(), end_location.toTuple(), mode="walking", departure_time=now)
  print(directions_response)
  return directions_response

def parse_directions_response(directions_response):
  if len(directions_response) > 0:
    route_response = directions_response[0]
    route_points = []
    route_distances = []
    route_durations = []
    route_polyline = route_response["overview_polyline"]["points"]

    legs = route_response["legs"]
    first_point = Location(latitude = legs[0]["steps"][0]["start_location"]["lat"], longitude = legs[0]["steps"][0]["start_location"]["lng"])
    route_points.append(first_point)

    for leg in legs:
      for step in leg["steps"]:
        new_point = Location(latitude = step["end_location"]["lat"], longitude = step["end_location"]["lng"])
        new_distance = step["distance"]["value"]  #distance from step's start to end in meters
        new_duration = step["duration"]["value"]  #duration from step's start to end in seconds
        route_points.append(new_point)
        route_distances.append(new_distance)
        route_durations.append(new_duration)

    print(route_points)
    print(len(route_points))
    print(route_distances)
    print(len(route_distances))
    return (route_points, route_distances, route_polyline)

  else:
    return "no routes, pick new points"

def print_reponse(response):
  pp = pprint.PrettyPrinter(depth=6)
  pp.pprint(reponse)


def main():
  location1 = Location(37.417747,-122.086086)
  location2 = Location(37.421624, -122.096472)
  route = Route(location1,location2)
  route.create_route()

if __name__ == '__main__':
	sys.exit(main())
