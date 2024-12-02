import time
import numpy as np
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Lidar, Electrics, Camera, AdvancedIMU
import keyboard
import threading
import random
import beamng_publisher
import zenoh

from shared import *

from pub.imu import send_imu_data
from scipy.spatial.transform import Rotation as R

intensity = 128
downsample_rate = 3

def send_lidar_data(lidar):
  data_publisher_instance = DataPublisherSingleton()
  vehicle_instance = VehicleSingleton()
  stop_event_instance = StopEventSingleton()
  
  lidar_hz = 10
  lidar_interval = 1.0 / lidar_hz
  base_time = time.time()
  
  while True:
    if stop_event_instance.get_value():
      break
    
    data = lidar.poll()
    pointcloud = data['pointCloud'][::downsample_rate]
    num_points = pointcloud.shape[0]
    
    if pointcloud is not None and len(pointcloud) > 0:
      vehicle_instance.get_sensor_data()
      state = vehicle_instance.get_state()
      position = lidar.get_position()
      relative_pointcloud = np.array(pointcloud - position, dtype=np.float32)
      
      rotation = state["rotation"]
      r = R.from_quat(rotation)
      yaw = r.as_euler('xyz', degrees=True)[2] + 90
      pitch = r.as_euler('xyz', degrees=True)[1]
      roll = r.as_euler('xyz', degrees=True)[0]
      new_rotation = R.from_euler('xyz', [roll, pitch, yaw], degrees=True)
      rotation_matrix = new_rotation.as_matrix()
      rotated_pointcloud = np.dot(relative_pointcloud, rotation_matrix.T)
      
      new_column_intensity = np.full((num_points, 1), intensity)
      
      pointcloud_4d = np.concatenate([rotated_pointcloud, new_column_intensity], axis=1).astype(np.float32)
      
      # pointcloud_4d = np.concatenate([relative_pointcloud, new_column_intensity], axis=1).astype(np.float32)
      
      data_publisher_instance.lidar(pointcloud_4d)
      
    next_time = max(0, lidar_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
  
def main():
  random.seed(1703)
  set_up_simple_logging()
  
  beamng = BeamNGpy('localhost', 64256)
  bng = beamng.open(launch=False)
  
  scenario = Scenario('2k_tsukuba_s', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  
  vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
  
  scenario.add_vehicle(vehicle,
          pos=(-103.2, -304.2, 74.0), rot_quat=(0,0,0.3826834,0.9238795)
  )
  
  # scenario = Scenario('west_coast_usa', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
  
  # vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
    
  # scenario.add_vehicle(vehicle,
  #     pos=(-717.121, 101, 118.675), rot_quat=(0, 0, 0.3826834, 0.9238795)
  # )
  
  scenario.make(bng)
  
  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()
  
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
  
  vehicle.sensors.attach('electrics', Electrics())
  
  stop_event = threading.Event()
  stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
  
  data_publisher_instance = DataPublisherSingleton()
  data_publisher_instance.set_data_publisher(beamng_publisher.BeamngPublisher())
  
  vehicle_instance = VehicleSingleton()
  vehicle_instance.set_vehicle(vehicle)

  stop_event_instance = StopEventSingleton()
  stop_event_instance.set_stop_event(stop_event)
  
  lidar_thread = threading.Thread(target=send_lidar_data, args=(lidar,))
  imu_thread = threading.Thread(target=send_imu_data, args=(imu,))
  
  stop_thread.start()
  lidar_thread.start()
  imu_thread.start()
  
  stop_thread.join()
  lidar_thread.join()
  imu_thread.join()
  
  lidar.remove()
  imu.remove()
  
if __name__ == '__main__':
    main()