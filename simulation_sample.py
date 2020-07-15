#!/usr/bin/env python3

import os
import sys

from geobeam.simulations import SimulationSetBuilder
from geobeam import generate_route
from geobeam import gps_utils

# TODO(ameles) change this to an actual config file and a script that uses those configs to make a simulation set
def main():
    # a 28 minute walk
  location1 = gps_utils.Location(37.417747, -122.086086)
  location2 = gps_utils.Location(37.421624, -122.096472)
  speed = 7  # meters/sec
  frequency = 10  # Hz
  file_name = "userwalking.csv"

  user_motion = generate_route.TimedRoute(location1, location2, speed, frequency)
  user_motion.write_route(file_name)

  file_path = os.path.abspath("geobeam/user_motion_files/" + file_name)

  simulation_set = (SimulationSetBuilder()
    .add_dynamic_route(file_path)
    .add_dynamic_route(file_path, run_duration=30, gain=-2)
    .add_static_route(27.417747, -112.086086, run_duration=10, gain=-2)
    .build())
  simulation_set.run_simulations()

if __name__ == "__main__":
  sys.exit(main())
