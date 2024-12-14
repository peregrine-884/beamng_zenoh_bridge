import random
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Electrics
import keyboard
import threading
import zenoh_bridge
import zenoh

from shared import *

from pub.clock import send_clock_data
from pub.vehicle_control import send_vehicle_control_data
from pub.vehicle_info import send_vehicle_info_data
from sub.model_control import model_control_callback
from calibration.calibration import create_accel_brake_map

def main():
  random.seed(1703)
  set_up_simple_logging()
  
  beamng = BeamNGpy('localhost', 64256)
  bng = beamng.open(launch=False)
  
  scenario = Scenario('tech_ground', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
  scenario.add_vehicle(vehicle,
    pos=(-1020.482, 0.000, 1.000), rot_quat=(0.0, 0.0, -0.70710678, 0.70710678)
  )
  
  scenario.make(bng)
  
  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()
  
  vehicle.sensors.attach('electrics', Electrics())
  
  config = zenoh.Config.from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
  session = zenoh.open(config)
  # key = 'rate_limitted/model/vehicle/command/actuation_cmd'
  # model_vehicle_control_sub = session.declare_subscriber(key, model_control_callback)
  
  stop_event = threading.Event()
  stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
  
  data_publisher_instance = DataPublisherSingleton()
  data_publisher_instance.set_data_publisher(zenoh_bridge.BeamngDataPublisher())
  
  vehicle_instance = VehicleSingleton()
  vehicle_instance.set_vehicle(vehicle)
  
  stop_event_instance = StopEventSingleton()
  stop_event_instance.set_stop_event(stop_event)
  
  vehicle_state_instance = VehicleStateSingleton()
  
  keyboard.on_press_key('s', 
        lambda event: vehicle_state_instance.set_manual_mode(not vehicle_state_instance.get_manual_mode()))
  
  clock_thread = threading.Thread(target=send_clock_data)
  vehicle_control_thread = threading.Thread(target=send_vehicle_control_data)
  vehicle_info_thread = threading.Thread(target=send_vehicle_info_data)
  get_vehicle_data_thread = threading.Thread(target=get_sensor_data)
  
  accel_brake_thread = threading.Thread(target=create_accel_brake_map)
  
  stop_thread.start()
  clock_thread.start()
  vehicle_control_thread.start()
  vehicle_info_thread.start()
  get_vehicle_data_thread.start()
  
  accel_brake_thread.start()
  
  stop_thread.join()
  clock_thread.join()
  vehicle_control_thread.join()
  vehicle_info_thread.join()
  get_vehicle_data_thread.join()
  
  accel_brake_thread.join()
  
  # model_vehicle_control_sub.undeclare()
  session.close()
  
if __name__ == '__main__':
  main()