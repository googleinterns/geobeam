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

"""Classes for Static and Dynamic Simulations, and for Simulation Sets.

  Typical usage example:
  simulation_set = (SimulationSetBuilder()
    .add_dynamic_route(file_path, gain=-2)
    .add_dynamic_route(file_path, run_duration=30, gain=-2)
    .add_static_route(27.417747, -112.086086, run_duration=10, gain=-2)
    .build())
  simulation_set.run_simulations()
"""

import csv
import datetime
import subprocess
import time

from tools import kbhit

KEYBOARD = kbhit.KBHit()
ONE_SEC = 1


class Simulation():
  """An object for a single GPS Simulation.

  """

  def __init__(self, run_duration=None, gain=None):
    """Initialize Simulation object

    Args:
      run_duration: int, simulation duration in seconds
      gain: float, signal gain for the broadcast by bladeRF board
    """
    self._run_duration = run_duration
    self._gain = gain
    self._process = None
    self._start_time = None
    self._end_time = None

  def run_simulation(self):
    """Starts bladeGPS subprocess using given simulation process arguments.
    """
    self._start_time = datetime.datetime.utcnow()
    self._process = create_bladeGPS_process(run_duration=self._run_duration, gain=self._gain)
    return

  def end_simulation(self):
    """Ends the bladeGPS subprocess.

    Checks if the process is still running, and then attempts to quit (via
    keyboard signal), terminate, and then kill the subprocess in that order
    """
    self._end_time = datetime.datetime.utcnow()
    while self.is_running():
      self._process.communicate(input="q".encode())
      print("Quitting simulation...")
      time.sleep(ONE_SEC)
      if self._process.poll() is None:
        print("Terminating subprocess...")
        self._process.terminate()
        time.sleep(ONE_SEC)
      if self._process.poll() is None:
        print("Killing subprocess...")
        self._process.kill()
        time.sleep(ONE_SEC)
    self._process = None
    print("Subprocess closed.")
    print("------------------------------------------------")

  def is_running(self):
    """Checks if there is bladeGPS subprocess currently running.

    Returns:
      True if there is a running process, False otherwise
    """
    return bool(self._process and self._process.poll() is None)

  def log_run(self, log_file_object):
    """Log start time, end time, type of simulation, and points.

    Logs timestamped file to open file_object with Simulation object string,
    start time, and end time

    Args:
      log_file_object: open file object to write to
    """
    start_time_string = self._start_time.isoformat()
    end_time_string = self._end_time.isoformat()
    fields = ["simulation_type", "run_duration", "gain", "start_time", "end_time"]
    values = [self.__class__.__name__, self._run_duration, self._gain, start_time_string, end_time_string]
    log_file_object.write("\n")
    csvwriter = csv.writer(log_file_object, delimiter=",")
    csvwriter.writerow(fields)
    csvwriter.writerow(values)

  def __repr__(self):
    return "Simulation(run_duration=%s, gain=%s)" % (self._run_duration, self._gain)


class StaticSimulation(Simulation):
  """An object for a single GPS Simulation for a static location.

  """

  def __init__(self, latitude, longitude, run_duration=None, gain=None):
    """Initialize Static Simulation.

    Args:
      run_duration: int, simulation duration in seconds
      gain: float, signal gain for the broadcast by bladeRF board
      latitude: float, static location latitude in decimal degrees
      longitude: float, static location longitude in decimal degrees
    """
    Simulation.__init__(self, run_duration, gain)
    self._latitude = latitude
    self._longitude = longitude

  def run_simulation(self):
    """Starts bladeGPS subprocess using given simulation process arguments.
    """
    self._start_time = datetime.datetime.utcnow()
    location = "%s,%s" % (self._latitude, self._longitude)
    self._process = create_bladeGPS_process(run_duration=self._run_duration,
                                            gain=self._gain,
                                            location=location)
    return

  def log_run(self, log_file_object):
    """Log start time, end time, type of simulation, and points.

    Logs timestamped file to open file_object with Simulation object string,
    start time, and end time

    Args:
      log_file_object: open file object to write to
    """
    start_time_string = self._start_time.isoformat()
    end_time_string = self._end_time.isoformat()
    fields = ["simulation_type", "latitude", "longitude", "run_duration", "gain", "start_time", "end_time"]
    values = [self.__class__.__name__, self._latitude, self._longitude,
              self._run_duration, self._gain, start_time_string, end_time_string]
    log_file_object.write("\n")
    csvwriter = csv.writer(log_file_object, delimiter=",")
    csvwriter.writerow(fields)
    csvwriter.writerow(values)

  def __repr__(self):
    return "StaticSimulation(latitude=%s, longitude=%s, run_duration=%s, gain=%s)" % (self._latitude,
                                                                                      self._longitude,
                                                                                      self._run_duration,
                                                                                      self._gain)


class DynamicSimulation(Simulation):
  """An object for a single GPS Simulation for a dynamic route.

  """

  def __init__(self, file_path, run_duration=None, gain=None):
    """An object for a single GPS Simulation for a static location.

    Args:
      run_duration: int, simulation duration in seconds
      gain: float, signal gain for the broadcast by bladeRF board
      file_path: absolute file path to user motion csv file for
      dynamic route simulation
    """
    Simulation.__init__(self, run_duration, gain)
    self._file_path = file_path

  def run_simulation(self):
    """Starts bladeGPS subprocess using simulation process arguments.
    """
    self._start_time = datetime.datetime.utcnow()
    self._process = create_bladeGPS_process(run_duration=self._run_duration,
                                            gain=self._gain,
                                            dynamic_file_path=self._file_path)
    return

  def log_run(self, log_file_object):
    """Log start time, end time, type of simulation, and points.

    Logs timestamped file to open file_object with Simulation object string,
    start and end time, and copy of the corresponding lines for that time frame
    from the user motion file used as input

    Args:
      log_file_object: open file object to write log to
    """
    start_time_string = self._start_time.isoformat()
    end_time_string = self._end_time.isoformat()
    fields = ["simulation_type", "file_path", "run_duration", "gain", "start_time", "end_time"]
    values = [self.__class__.__name__, self._file_path, self._run_duration,
              self._gain, start_time_string, end_time_string]
    log_file_object.write("\n")
    csvwriter = csv.writer(log_file_object, delimiter=",")
    csvwriter.writerow(fields)
    csvwriter.writerow(values)

    csvwriter.writerow(["time_from_zero", "x", "y", "z"])
    total_time = (self._end_time-self._start_time).total_seconds()
    route_file_path = self._file_path
    with open(route_file_path, "r") as route_file:
      lines_to_read = int(total_time*10)  # 10 points per second
      for _ in range(lines_to_read):
        try:
          log_file_object.write(next(route_file))
        except StopIteration:
          # reached end of source file
          break

  def __repr__(self):
    return "DynamicSimulation(file_path=%s, run_duration=%s, gain=%s)" % (self._file_path, self._run_duration, self._gain)


class SimulationSet():
  """An object for a set of GPS simulations (that can be dynamic or static).

  """

  def __init__(self, simulations):
    """An object for a set of GPS simulations (that can be dynamic or static).

    Set current_simulation_index to None and create unique log file name
    based on time stamp.

    Args:
      simulations: list of simulation objects in order of desired execution
    """
    self._simulations = simulations
    self._current_simulation_index = None
    now = datetime.datetime.utcnow()
    self._log_filename = now.strftime("GPSSIM-%Y-%m-%d_%H-%M-%S.csv")

  def run_simulations(self):
    """Starts simulations and navigates through according to user key press.

    Starts the first simulation, and then continuously checks if the current
    simulation is running, and switches to the next or previous based on
    keyboard input. If user presses q or last simulation finishes, it ends
    the simulation set
    """
    print("------------------------------------------------")
    print("Press 'n' to go to next sim, 'p' to go to previous sim, or 'q' to quit")
    print("------------------------------------------------")

    self._switch_simulation(0)
    while True:
      current_simulation = self._get_current_simulation()
      simulation_running = current_simulation.is_running()
      key_hit = key_pressed()
      #  quit via "q" press or end of last simulation
      if (key_hit == "q" or key_hit == "Q" or
          (not simulation_running and self._current_simulation_index >= len(self._simulations)-1)):
        current_simulation.end_simulation()
        self._log_current_simulation()
        break
      #  go to next simulation if "n" press or current sim ended
      elif key_hit == "n" or key_hit == "N" or not simulation_running:
        self._switch_simulation(self._current_simulation_index+1)
      # go to previous simulation if "p" press
      elif key_hit == "p" or key_hit == "P":
        self._switch_simulation(self._current_simulation_index-1)
    print("Simulation set ending...")
    self._current_simulation_index = None

  def _get_current_simulation(self):
    """Gets current simulation object.

    Returns:
      current simulation object if set has been started, None otherwise
    """
    if self._current_simulation_index is not None:
      return self._simulations[self._current_simulation_index]
    else:
      return None

  def _switch_simulation(self, new_simulation_index):
    """Switch to another simulation from the current simulation.

    Ends and logs current simulation, and then begins the new simulation
    and updates current simulation attributes

    Args:
      new_simulation_index: int for index desired simulation to be run
    """
    if new_simulation_index < len(self._simulations) and new_simulation_index >= 0:
      current_simulation = self._get_current_simulation()
      if (current_simulation):
        current_simulation.end_simulation()
        self._log_current_simulation()
      new_simulation = self._simulations[new_simulation_index]
      new_simulation.run_simulation()
      self._current_simulation_index = new_simulation_index
    elif new_simulation_index < 0:
      print("\nAlready on first simulation")
    else:
      print("\nAlready on last simulation")

  def _log_current_simulation(self):
    """Log start time, end time, type of simulation, and points (if dynamic).

    Logs timestamped file to simulation_logs directory with start and end time,
    whether the simulation was dynamic or static and the initialization arguments.
    If Dynamic, it copies the corresponding lines for that time frame from
    the user motion file used as input
    """
    log_file_path = "simulation_logs/" + self._log_filename
    with open(log_file_path, "a") as logfile:
      current_simulation = self._get_current_simulation()
      current_simulation.log_run(logfile)


class SimulationSetBuilder():
  """Builder for Simulation Set Objects.

  Attributes:
    simulations: list of simulation objects in order of desired execution
  """

  def __init__(self):
    self._simulations = []

  def add_static_route(self, latitude, longitude, run_duration=None, gain=None):
    """Creates a Static Simulation with correct arguments and adds to list.

    Returns:
      self object
    """
    self._simulations.append(StaticSimulation(latitude, longitude, run_duration, gain))
    return self

  def add_dynamic_route(self, file_path, run_duration=None, gain=None):
    """Creates a Dynamic Simulation with correct arguments and adds to list.

    Returns:
      self object
    """
    self._simulations.append(DynamicSimulation(str(file_path), run_duration, gain))
    return self

  def build(self):
    """Build SimulationSet object with list of simulations.

    Returns:
      A Simulation Set Object instantiated with current list of simulations
    """
    return SimulationSet(self._simulations)


def create_bladeGPS_process(run_duration=None, gain=None, location=None, dynamic_file_path=None):
  """Opens and returns the specified bladeGPS process based on arguments.
  Args:
    run_duration: int, time in seconds for how long simulation should run
    gain: float, signal gain for the broadcast by bladeRF board
    location: string, "%s,%s" % (latitude, longitude)
    dynamic_file_path: string, absolute file path to user motion csv file for
    dynamic route simulation
  Returns:
    subprocess called with command built from function inputs
  """
  command = ["./run_bladerfGPS.sh", "-T", "now"]
  if run_duration:
    command.append("-d")
    command.append(str(run_duration))
  if gain:
    command.append("-a")
    command.append(str(gain))
  if location:
    command.append("-l")
    command.append(location)
  elif dynamic_file_path:
    command.append("-u")
    command.append(dynamic_file_path)
  process = subprocess.Popen(command, stdin=subprocess.PIPE, cwd="./bladeGPS")
  return process


def key_pressed():
  """Uses Kbhit library to check if user has pressed key.

  Returns:
    a character (string) if a key has been pressed, None otherwise
  """
  pressed_char = None
  if KEYBOARD.kbhit():
    pressed_char = KEYBOARD.getch()
  return pressed_char

