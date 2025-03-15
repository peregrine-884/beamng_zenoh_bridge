import keyboard
import random
import threading
import time
import os
import sys
path_to_add = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path_to_add)

from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging

from beamng.utils.create_sensor_thread import create_sensor_thread
from beamng.vehicle.vehicle_data import VehicleData
from beamng.sensors import ImuManager, LidarManager

LIDAR_CONFIG = [  
  {
    "name": "top",
    "requested_update_time": 0.01,
    "pos": [0, 0.65, 2.0],
    "dir": [0, -1, 0],
    "up": [0, 0, 1],
    "vertical_resolution": 32,
    "horizontal_angle": 360,
    "is_rotate_mode": False,
    "is_360_mode": True,
    "is_using_shared_memory": True,
    "is_visualised": False,
    "is_streaming": True,
    "is_dir_world_space": False,
    "topic_name": "sensing/lidar/concatenated/pointcloud",
    "frequency": 10,
    "frame_id": "velodyne"
  }
]

IMU_CONFIG = [ 
  {
    "name": "imu",
    "gfx_update_time": 0.005,
    "pos": [0, 0.5, 0.45],
    "dir": [0, -1, 0],
    "up": [0, 0, 1],
    "is_send_immediately": True,
    "is_using_gravity": True,
    "is_visualised": True,
    "is_dir_world_space": False,
    "topic_name": "imu/data",
    "frequency": 25,
    "frame_id": "xsens_imu_link"
  }
]

def main():
  # configuration paths
  zenoh_config_path = os.path.join(path_to_add, 'config', 'zenoh', 'default.json5')
  
  # BeamNGpy setup
  random.seed(1703)
  set_up_simple_logging()
  beamng = BeamNGpy('localhost', 64256)
  bng = beamng.open(launch=False)
  
  scenario = Scenario('west_coast_usa', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  ego_vehicle = Vehicle('ego_vehicle', model='etk800', color='Blue')
  scenario.add_vehicle(ego_vehicle,
    pos=(-717.121, 101, 118.675),
    rot_quat=(0, 0, 0.3826834, 0.9238795)
  )
  
  scenario.make(bng)
  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()
  
  # Vehicle data setup
  ego_vehicle_data = VehicleData(ego_vehicle)
  
  # Setup sensors
  lidars = [LidarManager(bng, ego_vehicle, ego_vehicle_data, config, zenoh_config_path) for config in LIDAR_CONFIG]
  imus = [ImuManager(bng, ego_vehicle, config, zenoh_config_path) for config in IMU_CONFIG]
  
  # Stop event and keyboard listener
  stop_event = threading.Event()
  stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
  stop_thread.start()
  
  # Vehicle data thread
  get_vehicle_data_thread = threading.Thread(target=ego_vehicle_data.update_data, args=(stop_event, 10))
  get_vehicle_data_thread.start()
  
  # Wait for the vehicle to be ready
  while not(ego_vehicle_data.get_state() and ego_vehicle_data.get_electrics()):
    time.sleep(0.01)
    
  # Start sensor thread
  sensor_threads = []
  for sensor_manager in lidars + imus:
    sensor_threads.append(create_sensor_thread(sensor_manager, stop_event))
  
  # Wait for the stop event
  stop_thread.join()
  get_vehicle_data_thread.join()
  for sensor_thread in sensor_threads:
    sensor_thread.join()
    
  bng.close()
  
if __name__ == '__main__':
    main()