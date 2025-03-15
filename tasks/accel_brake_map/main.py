import keyboard
import threading
import random
import time
import os
import sys
path_to_add = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path_to_add)

from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging

from beamng.utils.create_sensor_thread import create_sensor_thread
from beamng.vehicle.vehicle_data import VehicleData
from beamng.vehicle.vehicle_interface import VehicleInterface
from beamng.sensors import ClockManager

from tasks.accel_brake_map.accel import accel_map
from tasks.accel_brake_map.brake import brake_map


CLOCK_CONFIG = {
  "topic_name": "clock",
  "frequency": 100
}

VEHICLE_INTERFACE_CONFIG = {
  'pub': {
    "actuation_status": {
      "topic_name": "vehicle/status/actuation_status",
      "frequency": 10
    },
    "steering_status": {
      "topic_name": "vehicle/status/steering_status",
      "frequency": 10
    },
    "velocity_status": {
      "topic_name": "vehicle/status/velocity_status",
      "frequency": 10
    }, 
  },
  'sub': {
    
  }
}

def main():
  # configuration paths
  zenoh_config_path = os.path.join(path_to_add, 'config', 'zenoh', 'default.json5')
  
  # BeamNGpy setup
  random.seed(1703)
  set_up_simple_logging()
  beamng = BeamNGpy('localhost', 64256)
  bng = beamng.open(launch=False)
  
  scenario = Scenario('tech_ground', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  ego_vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
  scenario.add_vehicle(ego_vehicle,
    pos=(-1020.482, 0.000, 1.000),
    rot_quat=(0.0, 0.0, -0.70710678, 0.70710678)
  )
  
  scenario.make(bng)
  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()
  
  # Vehicle data and interface setup
  ego_vehicle_data = VehicleData(ego_vehicle)
  ego_vehicle_interface = VehicleInterface(ego_vehicle, ego_vehicle_data, VEHICLE_INTERFACE_CONFIG, zenoh_config_path)
  
  # Sensor setup
  clock = ClockManager(CLOCK_CONFIG, zenoh_config_path)
  
  # Stop event and keyboard listener
  stop_event = threading.Event()
  stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
  stop_thread.start()
  
  # Start manual control toggle thread
  keyboard.on_press_key('s', lambda _: ego_vehicle_data.set_manual_mode(not ego_vehicle_data.get_manual_mode()))
  
  # Vehicle data thread
  get_vehicle_data_thread = threading.Thread(target=ego_vehicle_data.update_data, args=(stop_event, 10))
  get_vehicle_data_thread.start()
  
  # Wait for the vehicle to be ready
  while not(ego_vehicle_data.get_state() and ego_vehicle_data.get_electrics()):
    time.sleep(0.01)
    
  # Vehicle interface communication
  ego_vehicle_interface.start_communication(stop_event)
  
  # Start clock sensor thread
  clock_thread = create_sensor_thread(clock, stop_event)
    
  # Create Accel and Brake Map
  accel_map(ego_vehicle, ego_vehicle_data)
  brake_map(ego_vehicle, ego_vehicle_data)
    
  # Wait for the stop event
  stop_thread.join()
  get_vehicle_data_thread.join()
  ego_vehicle_interface.stop_communication()
  clock_thread.join()

if __name__ == '__main__':
  main()