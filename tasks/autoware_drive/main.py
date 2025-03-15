import os
import sys
import random
import threading
import keyboard
import time

# Zenoh configuration and BeamNG paths setup
path_to_add = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path_to_add)

from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamng.utils.config_loader import load_config_from_json5, split_data
from beamng.vehicle.vehicle_data import VehicleData
from beamng.vehicle.vehicle_interface import VehicleInterface
from beamng.sensors import CameraManager, ClockManager, GPSManager, ImuManager, LidarManager

def create_sensor_thread(sensor_manager, stop_event):
  """Function to create a thread for each sensor"""
  thread = threading.Thread(target=sensor_manager.send, args=(stop_event,))
  thread.start()
  return thread

def main():
  # Paths to the configuration files
  beamgng_config_dir = os.path.join(path_to_add, 'config', 'beamng')
  beamgng_config_file = 'base_config.json5'
  zenoh_config_path = os.path.join(path_to_add, 'config', 'zenoh', 'default.json5')

  # Load configuration
  beamng_config = load_config_from_json5(beamgng_config_dir, beamgng_config_file)
  level_config, ego_vehicle_config, npc_vehicles_config, sensors_config, vehicle_interface_config = split_data(beamng_config)

  # BeamNGpy setup
  random.seed(1703)
  set_up_simple_logging()
  beamng = BeamNGpy('localhost', 64256)
  bng = beamng.open(launch=False)

  scenario = Scenario(level_config['level'], level_config['description'])
  
  # Create ego vehicle
  ego_vehicle = Vehicle(ego_vehicle_config['name'], model=ego_vehicle_config['model'], color=ego_vehicle_config['color'])
  scenario.add_vehicle(ego_vehicle, pos=ego_vehicle_config['pos'], rot_quat=ego_vehicle_config['rot_quat'])
  
  # Create NPC vehicles
  npc_vehicles = []
  for npc_vehicle_config in npc_vehicles_config:
    npc_vehicle = Vehicle(npc_vehicle_config['name'], model=npc_vehicle_config['model'], color=npc_vehicle_config['color'])
    scenario.add_vehicle(npc_vehicle, pos=npc_vehicle_config['pos'], rot_quat=npc_vehicle_config['rot_quat'])
    npc_vehicles.append(npc_vehicle)
  
  scenario.make(bng)
  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()

  # Vehicle data and interface setup
  ego_vehicle_data = VehicleData(ego_vehicle)
  ego_vehicle_interface = VehicleInterface(ego_vehicle, ego_vehicle_data, vehicle_interface_config, zenoh_config_path)

  # Setup sensors
  print('======== Camera sensors ========')
  cameras = [CameraManager(bng, ego_vehicle, config, zenoh_config_path) for config in sensors_config['cameras']]
  
  print('======== Clock sensors ========')
  clocks = [ClockManager(config, zenoh_config_path) for config in sensors_config['clocks']]
  
  print('======== GPS sensors ========')
  gps = [GPSManager(bng, ego_vehicle, ego_vehicle_data, config, zenoh_config_path) for config in sensors_config['gps']]
  
  print('======== IMU sensors ========')
  imus = [ImuManager(bng, ego_vehicle, config, zenoh_config_path) for config in sensors_config['imus']]
  
  print('======== Lidar sensors ========')
  lidars = [LidarManager(bng, ego_vehicle, ego_vehicle_data, config, zenoh_config_path) for config in sensors_config['lidars']]

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

  # Vehicle interface communication
  ego_vehicle_interface.start_communication(stop_event)

  # Start sensor threads
  sensor_threads = []
  for sensor_manager in cameras + clocks + gps + imus + lidars:
    sensor_threads.append(create_sensor_thread(sensor_manager, stop_event))

  # Start manual control toggle thread
  keyboard.on_press_key('s', lambda event : ego_vehicle_data.set_manual_mode(not ego_vehicle_data.get_manual_mode()))

  # Wait for the stop signal and join threads
  stop_thread.join()
  get_vehicle_data_thread.join()
  ego_vehicle_interface.stop_communication()

  # Wait for all sensor threads to finish
  for thread in sensor_threads:
    thread.join()

if __name__ == '__main__':
  main()
