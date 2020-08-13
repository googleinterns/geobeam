#!/usr/bin/env python3

import configparser
import os
import sys

from geobeam.simulations import SimulationSetBuilder
from geobeam.generate_route import TimedRoute
from geobeam import gps_utils

# speed used as default config parser value if not specified by the user
DEFAULT_SPEED = "1.4"  # meters/sec
DEFAULT_FREQUENCY = 10  # Hz


def main(config_file_name):
  """Create and run simulation set based on user specified config file.

  Args:
    config_file_name: string, name of file in simulation_configs folder
    to read from
  """
  config = configparser.ConfigParser()
  config['DEFAULT']['Speed'] = DEFAULT_SPEED
  config_file_path = os.path.abspath("simulation_configs/" + config_file_name)
  config.read(config_file_path)

  sections = config.sections()

  simulation_set_builder = SimulationSetBuilder()

  for simulation in sections:
    try:
      run_duration = config.getint(simulation, "RunDuration", fallback=None)
      gain = config.getint(simulation, "Gain", fallback=None)

      # Dynamic Simulation
      if config.getboolean(simulation, "Dynamic"):

        file_name = config.get(simulation, "FileName")
        file_path = os.path.abspath("geobeam/user_motion_files/" + file_name)

        # Creating New Route File
        if config.getboolean(simulation, "CreateFile"):
          speed = config.getfloat(simulation, "Speed")
          frequency = DEFAULT_FREQUENCY
          if config.has_option(simulation, "GpxSourcePath"):
            gpx_source_path = config.get(simulation, "GpxSourcePath")
            user_motion = TimedRoute.from_gpx(gpx_source_path, speed, frequency)
          else:
            start_latitude = config.getfloat(simulation, "StartLatitude")
            start_longitude = config.getfloat(simulation, "StartLongitude")
            end_latitude = config.getfloat(simulation, "EndLatitude")
            end_longitude = config.getfloat(simulation, "EndLongitude")
            location1 = gps_utils.Location(start_latitude, start_longitude)
            location2 = gps_utils.Location(end_latitude, end_longitude)

            user_motion = TimedRoute.from_start_and_end(location1, location2, speed, frequency)
          user_motion.write_route(file_name)

        simulation_set_builder.add_dynamic_route(file_path,
                                                 run_duration=run_duration,
                                                 gain=gain)
      # Static Simulation
      else:
        latitude = config.getfloat(simulation, "Latitude")
        longitude = config.getfloat(simulation, "Longitude")
        simulation_set_builder.add_static_route(latitude, 
                                                longitude,
                                                run_duration=run_duration,
                                                gain=gain)
    except configparser.NoOptionError as err:
      print("Error in reading value from configuration file: %s" % err)
      return

  simulation_set = simulation_set_builder.build()
  simulation_set.run_simulations()

if __name__ == "__main__":
  sys.exit(main(sys.argv[1]))
