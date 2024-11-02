import numpy as np
from scipy.spatial.transform import Rotation as R
import time

from shared import *

intensity = 128
downsample_rate = 3
offset = np.array([0.3302292, 1.653519373, 0.12556159596657])

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
      position = state["pos"]
      relative_pointcloud = np.array(pointcloud - position + offset, dtype=np.float32)
      
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
      
      data_publisher_instance.lidar(pointcloud_4d)
      
    next_time = max(0, lidar_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
      