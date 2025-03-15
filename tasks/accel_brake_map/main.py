import random
import threading
import keyboard

import zenoh
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Electrics

import zenoh_bridge

from beamng.singleton_manager import (
  DataPublisherSingleton,
  StopEventSingleton,
  VehicleStateSingleton,
  VehicleSingleton
)
from beamng.pub import send_clock_data, send_vehicle_control_data, send_vehicle_info_data

from tasks.accel_brake_map.accel import accel_map
from tasks.accel_brake_map.brake import brake_map

def main():
  random.seed(1703)
  set_up_simple_logging()

  beamng = BeamNGpy('localhost', 64256)
  bng = beamng.open(launch=False)

  scenario = Scenario('tech_ground', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')

  scenario.add_vehicle(
    vehicle,
    pos=(-1020.482, 0.000, 1.000),
    rot_quat=(0.0, 0.0, -0.70710678, 0.70710678)
  )

  scenario.make(bng)

  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()

  vehicle.sensors.attach('electrics', Electrics())

  config = zenoh.Config.from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
  session = zenoh.open(config)

  stop_event = threading.Event()
  keyboard.add_hotkey('q', stop_event.set)

  data_publisher_instance = DataPublisherSingleton()
  data_publisher_instance.set_data_publisher(zenoh_bridge.BeamngDataPublisher())

  vehicle_instance = VehicleSingleton()
  vehicle_instance.set_vehicle(vehicle)

  stop_event_instance = StopEventSingleton()
  stop_event_instance.set_stop_event(stop_event)

  vehicle_state_instance = VehicleStateSingleton()
  
  keyboard.on_press_key('s', lambda _: vehicle_state_instance.set_manual_mode(
    not vehicle_state_instance.get_manual_mode()
  ))

  threads = [
    threading.Thread(target=send_clock_data),
    threading.Thread(target=send_vehicle_control_data),
    threading.Thread(target=send_vehicle_info_data),
    threading.Thread(target=get_sensor_data),
  ]

  for thread in threads:
    thread.start()

  accel_map()
  brake_map()

  for thread in threads:
    thread.join()

  session.close()

if __name__ == '__main__':
  main()