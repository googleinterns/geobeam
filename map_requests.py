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

"""Handles requests and parsing of Google Maps API calls

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""

import googlemaps
from datetime import datetime
import pprint
from config import api_key

API_KEY = api_key
gmaps = googlemaps.Client(key=API_KEY)

def request_directions(start_location,end_location):
  """request directions from start_location to end_location

  Args:
    start_location: tuple of floats (lat, lon) for starting point
    end_location: tuple of floats (lat, lon) for ending point
  Returns:
    a list of directions in the deserialized Maps API response format
  """ 
  now = datetime.now()
  directions_response= gmaps.directions(start_location, end_location, mode="walking", departure_time=now)
  print(directions_response)
  parsed_directions_response = parse_directions_response(directions_response)
  return parsed_directions_response

def parse_directions_response(directions_response):
  if len(directions_response) > 0:
    route_response = directions_response[0]
    route_points = []
    route_distances = []
    route_durations = []
    route_polyline = route_response["overview_polyline"]["points"]

    legs = route_response["legs"]
    first_point = (legs[0]["steps"][0]["start_location"]["lat"], legs[0]["steps"][0]["start_location"]["lng"])
    route_points.append(first_point)

    for leg in legs:
      for step in leg["steps"]:
        new_point = (step["end_location"]["lat"], step["end_location"]["lng"])
        new_distance = step["distance"]["value"]  #distance from step's start to end in meters
        new_duration = step["duration"]["value"]  #duration from step's start to end in seconds
        route_points.append(new_point)
        route_distances.append(new_distance)
        route_durations.append(new_duration)

    return (route_points, route_distances, route_durations, route_polyline)

  else:
    return "no routes, pick new points"

def request_elevations(locations):
  """request elevations for a list of (lat,lon) coordinates

  Args:
    locations: list of (lat,lon)
  Returns:
    a list of elevation responses in the deserialized Elevation API response format in order of input locations
  """
  elevations_response= gmaps.elevation(locations)
  print(elevations_response)
  parsed_elevations_response = parse_elevations_response(elevations_response)
  return parsed_elevations_response

def parse_elevations_response(elevations_response):
  elevations = []
  for result in elevations_response:
    elevations.append(result["elevation"])
  return elevations

def print_reponse(response):
  pp = pprint.PrettyPrinter(depth=6)
  pp.pprint(reponse)
