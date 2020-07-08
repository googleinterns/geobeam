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

"""Utilities for doing operations on GPS locations.
"""

import math

# World Geodetic System defined constants
_WGS84_EARTH_RADIUS = 6378137.0
_WGS84_ECCENTRICITY = 0.0818191908426


class Location():
  """An object for a location in the form of a set of coordinates.

  Attributes:
    latitude: a float for the latitude of the location in Decimal Degrees
    longitude: a float for the longitude of the location in Decimal Degrees
    altitude: a float for the altitude of the location in meters
    x: a float for the x coordinate of the location in ECEF format
    y: a float for the y coordinate of the location in ECEF format
    z: a float for the z coordinate of the location in ECEF format
  """

  def __init__(self, latitude, longitude, altitude=0):
    self.latitude = latitude
    self.longitude = longitude
    self.altitude = altitude
    self.x, self.y, self.z = geodetic_to_cartesian(self.latitude,
                                                   self.longitude,
                                                   self.altitude)

  def get_lat_lon_tuple(self):
    return (self.latitude, self.longitude)

  def get_xyz_tuple(self):
    return (self.x, self.y, self.z)

  def __repr__(self):
    return "Location(%s, %s, %s)" % (self.latitude, self.longitude,
                                     self.altitude)


def geodetic_to_cartesian(latitude, longitude, altitude):
  """Convert a single lat/lng/alt geodetic coordinate to ECEF cartesian coordinate.

  Produces earth-centered, earth-fixed (ECEF) cartesian coordinates from
  a geodetic coordinate (lat, lon, alt) and was adapted from c code in bladeGPS:
  https://github.com/osqzss/bladeGPS/blob/master/gpssim.c

  Args:
    latitude: float in Decimal Degrees
    longitude: float in Decimal Degrees
    altitude: float in meters

  Returns:
    location in ECEF format (x,y,z)
  """
  eccentricity_sq = _WGS84_ECCENTRICITY**2
  latitude_radians = math.radians(latitude)
  longitude_radians = math.radians(longitude)

  cos_latitude = math.cos(latitude_radians)
  sin_latitude = math.sin(latitude_radians)
  cos_longitude = math.cos(longitude_radians)
  sin_longitude = math.sin(longitude_radians)
  n_vector = _WGS84_EARTH_RADIUS/math.sqrt(1.0-(_WGS84_ECCENTRICITY*sin_latitude)**2)

  x = (n_vector + altitude)*cos_latitude*cos_longitude
  y = (n_vector + altitude)*cos_latitude*sin_longitude
  z = ((1.0-eccentricity_sq)*n_vector + altitude)*sin_latitude
  return (x, y, z)
