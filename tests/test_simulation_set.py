from datetime import datetime
import unittest
from unittest.mock import call
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import geobeam
from geobeam.simulations import DynamicSimulation
from geobeam.simulations import Simulation
from geobeam.simulations import StaticSimulation


class SimulationSetRunTests(unittest.TestCase):

  def setUp(self):
    simulation_one = create_autospec(Simulation)
    simulation_two = create_autospec(StaticSimulation)
    simulation_three = create_autospec(DynamicSimulation)
    self.simulations = [simulation_one, simulation_two, simulation_three]
    self.simulation_set = None
    self.mock_now = datetime(2020, 8, 15, 5, 0, 0)

  def update_index(self, index):
    self.simulation_set._current_simulation_index = index
    return

  @patch('geobeam.simulations.datetime.datetime')
  def test_simulation_set_init(self, mock_datetime):
    mock_datetime.utcnow.return_value = self.mock_now

    self.simulation_set = geobeam.simulations.SimulationSet(self.simulations)

    self.assertEqual(self.simulation_set._log_filename, "GPSSIM-2020-08-15_05-00-00.csv")

  @patch('geobeam.simulations.SimulationSet._get_current_simulation')
  @patch('geobeam.simulations.SimulationSet._log_current_simulation')
  @patch('geobeam.simulations.SimulationSet._switch_simulation')
  @patch('geobeam.simulations.key_pressed')
  @patch('geobeam.simulations.datetime.datetime')
  @patch('builtins.print')
  def test_run_simulations(self, mock_print, mock_datetime, mock_key_pressed,
                           mock_switch_simulation, mock_log_current_simulation,
                           mock_get_current_simulation):
    mock_datetime.utcnow.return_value = self.mock_now
    # 1 running, 2 running, 1 ends, 2 ends, 3 ends
    mock_key_pressed.side_effect = ["n", "p", None, None, None]
    mock_get_current_simulation.side_effect = [self.simulations[0],
                                               self.simulations[1],
                                               self.simulations[0],
                                               self.simulations[1],
                                               self.simulations[2]]
    self.simulations[0].is_running.side_effect = [True, False]
    self.simulations[1].is_running.side_effect = [True, False]
    self.simulations[2].is_running.side_effect = [False]
    mock_switch_simulation.side_effect = self.update_index
    self.simulation_set = geobeam.simulations.SimulationSet(self.simulations)

    self.simulation_set.run_simulations()

    self.assertIsNone(self.simulation_set._current_simulation_index)
    switch_calls = [call(0), call(1), call(0), call(1), call(2)]
    mock_switch_simulation.assert_has_calls(switch_calls)
    mock_log_current_simulation.assert_called_once()
    self.assertEqual(mock_get_current_simulation.call_count, 5)
    self.assertEqual(self.simulations[0].is_running.call_count, 2)
    self.assertEqual(self.simulations[1].is_running.call_count, 2)
    self.assertEqual(self.simulations[2].is_running.call_count, 1)

  @patch('geobeam.simulations.SimulationSet._get_current_simulation')
  @patch('geobeam.simulations.SimulationSet._log_current_simulation')
  @patch('geobeam.simulations.SimulationSet._switch_simulation')
  @patch('geobeam.simulations.key_pressed')
  @patch('geobeam.simulations.datetime.datetime')
  @patch('builtins.print')
  def test_run_simulations_quit_early(self, mock_print, mock_datetime, mock_key_pressed,
                                      mock_switch_simulation, mock_log_current_simulation,
                                      mock_get_current_simulation):
    mock_datetime.utcnow.return_value = self.mock_now
    # 1 running, 1 ends, 2 running, quit
    mock_key_pressed.side_effect = [None, None, None, "q"]
    mock_get_current_simulation.side_effect = [self.simulations[0],
                                               self.simulations[0],
                                               self.simulations[1],
                                               self.simulations[1]]
    self.simulations[0].is_running.side_effect = [True, False]
    self.simulations[1].is_running.side_effect = [True, True]
    mock_switch_simulation.side_effect = self.update_index
    self.simulation_set = geobeam.simulations.SimulationSet(self.simulations)

    self.simulation_set.run_simulations()

    self.assertIsNone(self.simulation_set._current_simulation_index)
    mock_switch_simulation.assert_has_calls([call(0), call(1)])
    mock_log_current_simulation.assert_called_once()
    self.assertEqual(mock_get_current_simulation.call_count, 4)
    self.assertEqual(self.simulations[0].is_running.call_count, 2)
    self.assertEqual(self.simulations[1].is_running.call_count, 2)
    self.assertEqual(self.simulations[2].is_running.call_count, 0)


class SimulationSetTest(unittest.TestCase):

  def setUp(self):
    simulation_one = create_autospec(Simulation)
    simulation_two = create_autospec(StaticSimulation)
    simulation_three = create_autospec(DynamicSimulation)
    self.simulations = [simulation_one, simulation_two, simulation_three]

  def test_get_current_simulation_not_running(self):
    simulation_set = geobeam.simulations.SimulationSet(self.simulations)
    simulation_set._current_simulation_index = None

    result = simulation_set._get_current_simulation()

    self.assertIsNone(result)

  def test_get_current_simulation(self):
    simulation_set = geobeam.simulations.SimulationSet(self.simulations)
    simulation_set._current_simulation_index = 1

    result = simulation_set._get_current_simulation()

    self.assertEqual(result, self.simulations[1])

  @patch('geobeam.simulations.SimulationSet._get_current_simulation')
  @patch('geobeam.simulations.datetime.datetime')
  def test_log_current_simulation(self, mock_datetime, mock_get_current_simulation):
    mock_now = datetime(2020, 8, 15, 5, 0, 0)
    mock_datetime.utcnow.return_value = mock_now
    simulation_set = geobeam.simulations.SimulationSet(self.simulations)
    mock_get_current_simulation.return_value = self.simulations[1]
    open_mock = mock_open()

    with patch("geobeam.simulations.open", open_mock, create=True):
      open_mock.return_value = MagicMock()
      simulation_set._log_current_simulation()

    self.simulations[1].log_run.assert_called_once()
    open_mock.assert_called_with("simulation_logs/GPSSIM-2020-08-15_05-00-00.csv", "a")

  @patch('geobeam.simulations.SimulationSet._get_current_simulation')
  @patch('geobeam.simulations.SimulationSet._log_current_simulation')
  def test_switch_simulation_from_start(self, mock_log_current_simulation, mock_get_current_simulation):
    simulation_set = geobeam.simulations.SimulationSet(self.simulations)
    mock_get_current_simulation.return_value = None
    simulation_set._current_simulation_index = None

    simulation_set._switch_simulation(0)

    mock_log_current_simulation.assert_not_called()
    self.simulations[0].run_simulation.assert_called_once()
    self.assertEqual(simulation_set._current_simulation_index, 0)

  @patch('geobeam.simulations.SimulationSet._get_current_simulation')
  @patch('geobeam.simulations.SimulationSet._log_current_simulation')
  def test_switch_simulation_next(self, mock_log_current_simulation, mock_get_current_simulation):
    simulation_set = geobeam.simulations.SimulationSet(self.simulations)
    mock_get_current_simulation.return_value = self.simulations[0]
    simulation_set._current_simulation_index = 0

    simulation_set._switch_simulation(1)

    mock_log_current_simulation.assert_called_once()
    self.simulations[0].end_simulation.assert_called_once()
    self.simulations[1].run_simulation.assert_called_once()
    self.assertEqual(simulation_set._current_simulation_index, 1)

  @patch('geobeam.simulations.SimulationSet._get_current_simulation')
  @patch('geobeam.simulations.SimulationSet._log_current_simulation')
  @patch('builtins.print')
  def test_switch_simulation_after_last(self, mock_print, mock_log_current_simulation, mock_get_current_simulation):
    simulation_set = geobeam.simulations.SimulationSet(self.simulations)
    mock_get_current_simulation.return_value = self.simulations[2]
    simulation_set._current_simulation_index = 2

    simulation_set._switch_simulation(3)

    mock_log_current_simulation.assert_not_called()
    self.simulations[2].end_simulation.assert_not_called()
    self.simulations[2].run_simulation.assert_not_called()
    self.assertEqual(simulation_set._current_simulation_index, 2)
    mock_print.assert_called_once_with("\nAlready on last simulation")

  @patch('geobeam.simulations.SimulationSet._get_current_simulation')
  @patch('geobeam.simulations.SimulationSet._log_current_simulation')
  @patch('builtins.print')
  def test_switch_simulation_before_first(self, mock_print, mock_log_current_simulation, mock_get_current_simulation):
    simulation_set = geobeam.simulations.SimulationSet(self.simulations)
    mock_get_current_simulation.return_value = self.simulations[0]
    simulation_set._current_simulation_index = 0

    simulation_set._switch_simulation(-1)

    mock_log_current_simulation.assert_not_called()
    self.simulations[0].end_simulation.assert_not_called()
    self.simulations[0].run_simulation.assert_not_called()
    self.assertEqual(simulation_set._current_simulation_index, 0)
    mock_print.assert_called_once_with("\nAlready on first simulation")

  @patch('geobeam.simulations.KEYBOARD')
  def test_key_pressed_not_pressed(self, mock_keyboard):
    mock_keyboard.kbhit.return_value = False
    mock_keyboard.getch.return_value = 'n'

    result = geobeam.simulations.key_pressed()

    self.assertIsNone(result)
    mock_keyboard.getch.assert_not_called()

  @patch('geobeam.simulations.KEYBOARD')
  def test_key_pressed(self, mock_keyboard):
    mock_keyboard.kbhit.return_value = True
    mock_keyboard.getch.return_value = 'n'

    result = geobeam.simulations.key_pressed()

    self.assertEqual(result, 'n')
    mock_keyboard.getch.assert_called_once()
