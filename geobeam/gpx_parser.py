# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

"""Extract Geolocation Points from GPX File.
"""
import os

import xml.etree.ElementTree as ET

# prefix url in xml file
PREFIX_URL = "{http://www.topografix.com/GPX/1/1}"


class GpxFileParser:

  def parse_file(self, file_path):
    """Traverses the xml tree and extracts GPX trackpoints.

    Args:
      file_path: name of the xml/gpx file

    Returns:
      a list of (lat, lon, alt) tuples extracted from Gpx file
    """
    file_type = self._get_file_type(file_path)

    if file_type == ".xml" or file_type == ".gpx":
      with open(file_path, "r") as gpx_file:
        gpx_tree = ET.parse(gpx_file)

      root = gpx_tree.getroot()

      # parse to get list of gps location points
      gpx_points = self._parse_gpx_trkpts(root, PREFIX_URL)

      return gpx_points

    else:
      print("Invalid file type. Accepted: xml, gpx. Received: " + file_type)
      return None

  def _get_file_type(self, file_path):
    """Get the file type (extension).

    Args:
      file_path: name of the xml/gpx file

    Returns:
      string, file extension
    """
    if file_path:
      file_type = os.path.splitext(file_path)[1]
    else:
      return None

    return file_type

  def _parse_gpx_trkpts(self, root, prefix) -> []:
    """Helper function to parse trkpts in gpx file.

    Args:
      root: root of xml tree
      prefix: string, prefix url

    Returns:
      a list of (lat, lon, alt) tuples extracted from Gpx file
    """
    gpx_points = []

    trk = root.find(prefix + "trk")
    if trk is None:
      print("trk is None, could not parse trkpts.")
      return None

    trkseg = trk.find(prefix + "trkseg")
    if trkseg is None:
      print("trkseg is None, could not parse trkpts.")
      return None

    if len(trkseg) == 0:
      print("trkseg is empty, could not parse trkpts.")
      return None

    prev_altitude = 0

    # Get every track point information
    for trkpt in trkseg:
      # Get the latitude and longitude
      lat = float(trkpt.get("lat"))
      lon = float(trkpt.get("lon"))

      # if no altitude value, make it same as previous point's altitude
      altitude = prev_altitude

      for data in trkpt.iter():
        if data.tag == prefix + "ele":
          altitude = float(data.text)
          prev_altitude = altitude

      current_location = (lat, lon, altitude)
      gpx_points.append(current_location)

    return gpx_points
