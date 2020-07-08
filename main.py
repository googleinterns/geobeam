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

import sys

from generate_route import Route
from generate_route import TimedRoute
from gps_utils import Location

#meters per second
TRANSPORT_SPEEDS = {"walking": 1.4, "running": 2.5, "biking": 7}
10_HZ = 10


def main():
  # a 28 minute walk
  location1 = Location(37.417747, -122.086086)
  location2 = Location(37.421624, -122.096472)

  # gives 14 points of information straight from api
  route = Route(location1, location2)
  route.write_route("routetestfile.csv")

  # gives 16459 points at 7 points/meter & 10 points/second
  user_motion = TimedRoute(location1, location2, TRANSPORT_SPEEDS["walking"], 10_HZ)
  user_motion.write_route("userwalking.csv")

  # gives 9226 points at 4 points/meter & 10 points/second
  user_motion = TimedRoute(location1, location2, TRANSPORT_SPEEDS["running"], 10_HZ)
  user_motion.write_route("userrunning.csv")

  # gives 3289 points at 1.4 points/meter & 10 points/second
  user_motion = TimedRoute(location1, location2, TRANSPORT_SPEEDS["biking"], 10_HZ)
  user_motion.write_route("userbiking.csv")

if __name__ == "__main__":
  sys.exit(main())
