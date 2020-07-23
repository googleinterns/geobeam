from datetime import datetime
import unittest
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch

import geobeam


class SimulationTest(unittest.TestCase):

  def setUp(self):
    self.run_duration = 100
    self.gain = -2
    self.start_time = datetime(2020, 8, 15, 5, 0, 0)
    self.end_time = datetime(2020, 8, 15, 5, 1, 10)
    self.latitude = 27.12345
    self.longitude = -37.45678
    self.location = "27.12345,-37.45678"
    self.file_path = "/home/fakeuser/Desktop/geobeam/geobeam/user_motion_files/testfile.csv"

  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.create_bladeGPS_process')
  def test_run_simulation(self, mock_create_bladeGPS_process, mock_datetime):
    mock_datetime.utcnow.return_value = self.start_time
    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation.run_simulation()
    self.assertEqual(test_simulation._start_time, self.start_time)
    mock_datetime.utcnow.assert_called_once()
    mock_create_bladeGPS_process.assert_called_once_with(run_duration=self.run_duration, gain=self.gain)

  @patch('geobeam.simulations.time')
  @patch('builtins.print')
  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_end_simulation_running_quit(self, mock_subprocess, mock_datetime,
                                       mock_print, mock_time):
    mock_datetime.utcnow.return_value = self.end_time
    mock_subprocess.poll.side_effect = [0, 0]

    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = mock_subprocess
    test_simulation.is_running = Mock(side_effect=[True, False])
    test_simulation.end_simulation()

    self.assertIsNone(test_simulation._process)
    self.assertEqual(test_simulation._end_time, self.end_time)

    mock_subprocess.communicate.assert_called_once()
    mock_subprocess.terminate.assert_not_called()
    mock_subprocess.kill.assert_not_called()
    self.assertEqual(mock_subprocess.poll.call_count, 2)

    self.assertEqual(mock_time.sleep.call_count, 1)

  @patch('geobeam.simulations.time')
  @patch('builtins.print')
  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_end_simulation_running_terminate(self, mock_subprocess, mock_datetime,
                                            mock_print, mock_time):
    mock_datetime.utcnow.return_value = self.end_time
    mock_subprocess.poll.side_effect = [None, 0]

    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = mock_subprocess
    test_simulation.is_running = Mock(side_effect=[True, False])
    test_simulation.end_simulation()

    self.assertIsNone(test_simulation._process)
    self.assertEqual(test_simulation._end_time, self.end_time)

    mock_subprocess.communicate.assert_called_once()
    mock_subprocess.terminate.assert_called_once()
    mock_subprocess.kill.assert_not_called()
    self.assertEqual(mock_subprocess.poll.call_count, 2)

    self.assertEqual(mock_time.sleep.call_count, 2)

  @patch('geobeam.simulations.time')
  @patch('builtins.print')
  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_end_simulation_running_terminate_and_kill(self, mock_subprocess, 
                                                     mock_datetime, mock_print, mock_time):
    mock_datetime.utcnow.return_value = self.end_time
    mock_subprocess.poll.side_effect = [None, None]

    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = mock_subprocess
    test_simulation.is_running = Mock(side_effect=[True, False])
    test_simulation.end_simulation()

    self.assertIsNone(test_simulation._process)
    self.assertEqual(test_simulation._end_time, self.end_time)

    mock_subprocess.communicate.assert_called_once()
    mock_subprocess.terminate.assert_called_once()
    mock_subprocess.kill.assert_called_once()
    self.assertEqual(mock_subprocess.poll.call_count, 2)

    self.assertEqual(mock_time.sleep.call_count, 3)

  @patch('geobeam.simulations.time')
  @patch('builtins.print')
  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_end_simulation_done_running(self, mock_subprocess, mock_datetime, 
                                       mock_print, mock_time):
    mock_datetime.utcnow.return_value = self.end_time

    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = mock_subprocess
    test_simulation.is_running = Mock(return_value=False)
    test_simulation.end_simulation()

    self.assertIsNone(test_simulation._process)
    self.assertEqual(test_simulation._end_time, self.end_time)

    mock_subprocess.communicate.assert_not_called()
    mock_subprocess.terminate.assert_not_called()
    mock_subprocess.kill.assert_not_called()
    mock_subprocess.poll.assert_not_called()
    mock_time.sleep.assert_not_called()

  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_is_running_with_running_process(self, mock_subprocess, mock_datetime):
    # current process is running
    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = mock_subprocess
    mock_subprocess.poll.return_value = None

    result = test_simulation.is_running()

    self.assertTrue(result)

  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_is_running_with_no_process(self, mock_subprocess, mock_datetime):
    # no current process
    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = None
    mock_subprocess.poll.return_value = 0

    result = test_simulation.is_running()

    self.assertFalse(result)

  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_is_running_process_and_poll_none(self, mock_subprocess, mock_datetime):
    # no current process
    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = None
    mock_subprocess.poll.return_value = None

    result = test_simulation.is_running()

    self.assertFalse(result)

  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.subprocess')
  def test_is_running_process_finished(self, mock_subprocess, mock_datetime):
    # current process already finished
    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._process = mock_subprocess
    mock_subprocess.poll.return_value = 0

    result = test_simulation.is_running()

    self.assertFalse(result)

  @patch('geobeam.simulations.csv')
  def test_log_run(self, mock_csv):
    mock_logfile = Mock()
    mock_logfile.write = Mock()
    test_simulation = geobeam.simulations.Simulation(self.run_duration, self.gain)
    test_simulation._start_time = self.start_time
    test_simulation._end_time = self.end_time
    fields = ["simulation_type", "run_duration", "gain", "start_time", "end_time"]
    values = ["Simulation", self.run_duration, self.gain, "2020-08-15T05:00:00", "2020-08-15T05:01:10"]
    csv_calls = [call(fields), call(values)]

    test_simulation.log_run(mock_logfile)

    mock_logfile.write.assert_called_once_with('\n')
    mock_csv.writer.assert_called_once()
    mock_csv.writer().writerow.assert_has_calls(csv_calls)

  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.create_bladeGPS_process')
  def test_run_static_simulation(self, mock_create_bladeGPS_process, mock_datetime):
    mock_datetime.utcnow.return_value = self.start_time
    test_simulation = geobeam.simulations.StaticSimulation(self.latitude,
                                                           self.longitude,
                                                           self.run_duration,
                                                           self.gain)
    test_simulation.run_simulation()
    self.assertEqual(test_simulation._start_time, self.start_time)
    mock_datetime.utcnow.assert_called_once()
    mock_create_bladeGPS_process.assert_called_once_with(run_duration=self.run_duration,
                                                         gain=self.gain,
                                                         location=self.location)
  
  @patch('geobeam.simulations.csv')
  def test_log_static_run(self, mock_csv):
    mock_logfile = Mock()
    mock_logfile.write = Mock()
    test_simulation = geobeam.simulations.StaticSimulation(self.latitude,
                                                           self.longitude,
                                                           self.run_duration,
                                                           self.gain)
    test_simulation._start_time = self.start_time
    test_simulation._end_time = self.end_time
    fields = ["simulation_type", "latitude", "longitude", "run_duration", "gain", "start_time", "end_time"]
    values = ["StaticSimulation", self.latitude, self.longitude, self.run_duration, self.gain, "2020-08-15T05:00:00", "2020-08-15T05:01:10"]
    csv_calls = [call(fields), call(values)]

    test_simulation.log_run(mock_logfile)

    mock_logfile.write.assert_called_once_with('\n')
    mock_csv.writer.assert_called_once()
    mock_csv.writer().writerow.assert_has_calls(csv_calls)

  @patch('geobeam.simulations.datetime.datetime')
  @patch('geobeam.simulations.create_bladeGPS_process')
  def test_run_dynamic_simulation(self, mock_create_bladeGPS_process, mock_datetime):
    mock_datetime.utcnow.return_value = self.start_time
    test_simulation = geobeam.simulations.DynamicSimulation(self.file_path,
                                                            self.run_duration,
                                                            self.gain)

    test_simulation.run_simulation()

    self.assertEqual(test_simulation._start_time, self.start_time)
    mock_datetime.utcnow.assert_called_once()
    mock_create_bladeGPS_process.assert_called_once_with(run_duration=self.run_duration,
                                                         gain=self.gain,
                                                         dynamic_file_path=self.file_path)
  
  @patch('geobeam.simulations.csv')
  def test_log_dynamic_run(self, mock_csv):
    mock_logfile = Mock()
    mock_logfile.write = Mock()
    test_simulation = geobeam.simulations.DynamicSimulation(self.file_path,
                                                            self.run_duration,
                                                            self.gain)
    self.start_time = datetime(2020, 8, 15, 5, 0, 0)
    self.end_time = datetime(2020, 8, 15, 5, 0, 10)
    test_simulation._start_time = self.start_time
    test_simulation._end_time = self.end_time

    open_mock = mock_open()
    with patch("geobeam.simulations.open", open_mock, create=True):
      open_mock.return_value = MagicMock()
      test_simulation.log_run(mock_logfile)

    mock_csv.writer.assert_called_once()
    fields = ["simulation_type", "file_path", "run_duration", "gain", "start_time", "end_time"]
    values = ["DynamicSimulation", self.file_path, self.run_duration, self.gain, "2020-08-15T05:00:00", "2020-08-15T05:00:10"]
    gps_fields = ["time_from_zero", "x", "y", "z"]
    csv_calls = [call(fields), call(values), call(gps_fields)]
    mock_csv.writer().writerow.assert_has_calls(csv_calls)

    open_mock.assert_called_with(self.file_path, "r")
    self.assertEqual(mock_logfile.write.call_args_list[0], call('\n'))
    # check for 1 blank line call and 100 copied lines for 10 seconds of data
    self.assertEqual(mock_logfile.write.call_count, 101)

  @patch('geobeam.simulations.subprocess')
  def test_create_blade_GPS_process(self, mock_subprocess):
    mock_subprocess.Popen = Mock()
    mock_subprocess.PIPE = Mock()

    commands = [["./run_bladerfGPS.sh", "-T", "now"],
                ["./run_bladerfGPS.sh", "-T", "now", "-d", "20"],
                ["./run_bladerfGPS.sh", "-T", "now", "-a", "-2"],
                ["./run_bladerfGPS.sh", "-T", "now", "-u", "test/path"],
                ["./run_bladerfGPS.sh", "-T", "now", "-d", "20", "-a", "-2"],
                ["./run_bladerfGPS.sh", "-T", "now", "-d", "20", "-a", "-2", "-l", "27.12345,-37.45678"],
                ["./run_bladerfGPS.sh", "-T", "now", "-d", "20", "-a", "-2", "-u", "test/path"],
                ["./run_bladerfGPS.sh", "-T", "now", "-d", "20", "-a", "-2", "-l", "27.12345,-37.45678"]]

    results = [geobeam.simulations.create_bladeGPS_process(),
               geobeam.simulations.create_bladeGPS_process(run_duration=20),
               geobeam.simulations.create_bladeGPS_process(gain=-2),
               geobeam.simulations.create_bladeGPS_process(dynamic_file_path="test/path"),
               geobeam.simulations.create_bladeGPS_process(run_duration=20, gain=-2),
               geobeam.simulations.create_bladeGPS_process(run_duration=20, gain=-2,
                                                           location="27.12345,-37.45678"),
               geobeam.simulations.create_bladeGPS_process(run_duration=20, gain=-2, 
                                                           dynamic_file_path="test/path"),
               geobeam.simulations.create_bladeGPS_process(run_duration=20, gain=-2,
                                                           location="27.12345,-37.45678",
                                                           dynamic_file_path="test/path")]
    for i in range(len(commands)):
      self.assertEqual(mock_subprocess.Popen.call_args_list[i][0][0], commands[i])
      self.assertEqual(results[i], mock_subprocess.Popen())

