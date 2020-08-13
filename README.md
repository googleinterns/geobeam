# Geobeam

An economical GPS simulator that can produce a deterministic signal.

## Setup

1. Clone this repo
2. Setup Hardware
    * Connect Antenna into TX1 Port of the BladeRF software defined radio board (tested on micro xA4, but should work with others)
    * Use SuperSpeed USB 3.0 cable to plug the board into the computer
2. After cloning geobeam, clone the bladeGPS and bladeRF repositories into the repo folder.
    ```
    git clone https://github.com/Nuand/bladeRF.git
    git clone https://github.com/osqzss/bladeGPS
    ```
    Follow setup intructions for setting up and making bladeRF and bladeGPS [here](https://github.com/osqzss/bladeGPS).
    Your directory structure should look like this:
    ```
    ├── geobeam
    │   ├── bladeGPS
    │   ├── bladeRF
    │   ├── docs
    │   ├── geobeam
    │   ├── LICENSE
    │   ├── README.md
    │   ├── run.py
    │   ├── simulation_configs
    │   ├── tests
    │   └── tools
    ```

3. Make a NASA Earthdata account:

    Register at https://urs.earthdata.nasa.gov/
    Your first time running geobeam, it should create a text file named .wgetrc inside the bladeGPS folder where you can input your username and password for     this account like so:
    ```
    http_user=fake_username
    http_password=fake_password
    ```
    This account is needed to download the daily ephemeris files used to simulate the satellite locations.
  
## Creating a configuration file

To run a set of simulations, you can create a configuration file in geobeam/simulation_configs with a .ini file extension

Each simulation should be placed under a uniquely named header like so:

sample_configuration.ini
```
[SimulationOne]
Dynamic = True
CreateFile = True
FileName = sample_run.csv
StartLatitude = 40.794195
StartLongitude = -73.963177
EndLatitude = 40.731278
EndLongitude = -73.999541
Speed = 2.7
Gain = -2

[SimulationTwo]
Dynamic = True
CreateFile = False
FileName = sample_walk.csv
Gain = -4
RunDuration = 120

[SimulationThree]
Dynamic = False
Latitude = 40.731278
Longitude = -73.999541
Gain = -2

[SimulationFour]
Dynamic = True
CreateFile = True
FileName = sample_run_from_gpx.csv
GpxSourcePath = path/to/file/sample_run.gpx
Speed = 2.7
Gain = -2
```

This configuration file has, in order:
* a Dynamic Simulation using newly created dynamic route with a speed of 2.7 meters per second that will be saved to sample_run.csv and run
* a Dynamic Simulationpremade dynamic route called sample_walk.csv that will be run for 120 seconds
* a Static Simulation of the point (40.731278, -73.999541)
* a Dynamic Simulation using a newly created dynamic route that was created from points extracted from the user provided sample_run.gpx GPX file

All route files are created with a default frequency of 10 Hz to match the simulator input format.

**Common Configuration Properties:**
* _Dynamic_: True if Dynamic Simulation, False if Static
* _Gain_: integer for broadcast signal gain value
* _RunDuration_: integer in seconds for how long to run the simulation

**Dynamic-Specific Configuration Properties:**
* _CreateFile_: True if creating new route file, False if using route file that has already been created
* _FileName_: name of route file to be saved or used
* _Speed_: speed with which the newly created route is traversed in meters/second
* If creating route from two endpoints (all floats in decimal degrees):
  * _StartLatitude_
  * _StartLongitude_
  * _EndLatitude_
  * _EndLongitude_
* If creating route from a GPX File:
  * _GpxSourcePath_: absolute path to desired gpx file

**Static-Specific Configuration Properties:**
* _Latitude_: float in decimal degrees
* _Longitude_: float in decimal degrees

## Running a Simulation Set

Inside of the project repository, make _run.py_ an executable and run:
```
chmod +x run.py
./run.py <configuration_file_name>
```
Or just `python3 run.py <configuration_file_name>`

For example: 

`./run.py sample_configuration.ini`

## Creating User Motion Files

If you want to create user motion files independently of creating a configuration file that will do so, follow the template shown in _geobeam/geobeam/main.py_.
You can replace with the desired route from start and endpoints or from GPX:
```
location1 = Location(40.794195, -73.963177)
location2 = Location(40.731278, -73.999541)

# arguments: start location, end location, speed in m/s, frequency (simulator uses 10 Hz)
user_motion = TimedRoute.from_start_and_end(location1, location2, 1.4, TEN_HZ)
user_motion.write_route("sample_walking.csv")

user_motion = TimedRoute.from_start_and_end(location1, location2, 2.7, TEN_HZ)
user_motion.write_route("sample_running.csv")

# arguments: path to gpx file, speed in m/s, frequency (simulator uses 10 Hz)
user_motion = TimedRoute.from_gpx("/path/to/gpx/sample_file.gpx", 2.7, TEN_HZ)
user_motion.write_route("sample_running_from_gpx.csv")
```
And run file with `python3 -m geobeam.main`. It will create the user motion files in the _geobeam/geobeam/user_motion_files_ directory and can then be fed into the simulator.

## Running Tests

Inside of the project repository run `python3 -m unittest discover tests -b`
