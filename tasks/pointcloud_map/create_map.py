import time
import random
import threading
import keyboard

import numpy as np
from scipy.spatial.transform import Rotation as R

from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Lidar, Electrics, AdvancedIMU

import zenoh_bridge

from core.singleton_manager import (
   DataPublisherSingleton,
   StopEventSingleton,
   VehicleSingleton
)
from core.pub import send_imu_data, send_lidar_data

def main():
  random.seed(1703)
  set_up_simple_logging()
  
  beamng = BeamNGpy('localhost', 64256)
  bng = beamng.open(launch=False)
  
  # scenario = Scenario('west_coast_usa', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  # vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue') 
  # scenario.add_vehicle(vehicle,
  #     pos=(-717.121, 101, 118.675), rot_quat=(0, 0, 0.3826834, 0.9238795)
  # )
  
  # scenario = Scenario('2k_tsukuba', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  # vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
  # scenario.add_vehicle(vehicle,
  #         pos=(-97.2, -304.2, 74.0), rot_quat=(0,0,0.3826834,0.9238795)
  # )
  
  # scenario = Scenario('c1', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  # vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
  # vehicle2 = Vehicle('object', model='etk800', license='RED', color='RED')
  # vehicle3 = Vehicle('object2', model='etk800', license='RED', color='GREEN')
  
  # scenario.add_vehicle(vehicle,
  #           pos=(-5955.8, -13987.0, 897.8), rot_quat=(0.0, 0.0, -0.91706007, 0.39874907)
  # )
  
  scenario = Scenario('2k_tsukuba', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
  scenario.add_vehicle(vehicle,
        pos=(-96.2, -304.7, 73.7), rot_quat=(0.0, 0.0, 0.35836795, 0.93358043)
    )
  vehicle2 = Vehicle('ego_vehicle2', model='etk800', license='RED', color='Red') 
  scenario.add_vehicle(vehicle2,
      pos=(-104.04, -305.19, 74.5), rot_quat=(0.0, 0.0, 0.35836795, 0.93358043)
  )

  scenario.make(bng)
  
  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()
  
  # vehicle.ai.set_mode("traffic")
  # vehicle.ai.set_speed(3)
  
  lidar = Lidar(
    'lidar1',
    bng,
    vehicle,
    requested_update_time=0.01,
    pos=(0, 0.65, 2.0),
    dir=(0, -1, 0),
    up=(0, 0, 1),
    vertical_resolution=32,
    horizontal_angle=360,
    is_rotate_mode=False,
    is_360_mode=True,
    is_using_shared_memory=True,
    is_visualised=False,
    is_streaming=True,
    is_dir_world_space=False
  )
  
  imu = AdvancedIMU(
    'imu',
    bng,
    vehicle,
    gfx_update_time=0.005,
    pos=(0, 0.5, 0.45),
    dir=(0, -1, 0),
    up=(-0, 0, 1),
    is_send_immediately=True,
    is_using_gravity=True,
    is_visualised=True,
    is_dir_world_space=False,
  )
  
  ref_lon, ref_lat = 0.0, 0.0
  gps_front = GPS(
      "front",
      bng,
      vehicle,
      pos=(0, -1.5, 1.0),
      ref_lon=ref_lon,
      ref_lat=ref_lat,
      is_visualised=True,
  )
  
  vehicle.sensors.attach('electrics', Electrics())
  
  stop_event = threading.Event()
  stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
  
  data_publisher_instance = DataPublisherSingleton()
  data_publisher_instance.set_data_publisher(zenoh_bridge.BeamngDataPublisher())
  
  vehicle_instance = VehicleSingleton()
  vehicle_instance.set_vehicle(vehicle)

  stop_event_instance = StopEventSingleton()
  stop_event_instance.set_stop_event(stop_event)
  
  lidar_thread = threading.Thread(target=send_lidar_data, args=(lidar, "velodyne"))
  imu_thread = threading.Thread(target=send_imu_data, args=(imu,))
  get_vehicle_data_thread = threading.Thread(target=get_sensor_data)
  gps_thread = threading.Thread(target=send_gps, args=(gps_front,))
  
  stop_thread.start()
  lidar_thread.start()
  imu_thread.start()
  get_vehicle_data_thread.start()
  gps_thread.start()
  
  threads = [
      stop_thread,
      imu_thread,
      lidar_thread,
      get_vehicle_data_thread,
      gps_thread
  ]
  while any(thread.is_alive() for thread in threads):
      print(", ".join(f"{thread.name} {'is running' if thread.is_alive() else 'has finished'}" for thread in threads))
      time.sleep(1)
  
  stop_thread.join()
  lidar_thread.join()
  imu_thread.join()
  gps_thread.join()
  
  lidar.remove()
  imu.remove()
  bng.close()
  
if __name__ == '__main__':
    main()