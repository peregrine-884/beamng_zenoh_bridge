import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from beamngpy.sensors import Lidar

from core.singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleSingleton

class Lidarmanager:
  INTENSITY = 128
  DOWNSAMPLE_RATE = 5
  OFFSET = np.array([0.3302292, 1.653519373, 0.12556159596657])

  def __init__(self, bng, vehicle, lidar_data, frame):
    self.lidar = Lidar(
      lidar_data['name'],
      bng,
      vehicle,
      requested_update_time=lidar_data['requested_update_time'],
      pos=tuple(lidar_data['pos']), 
      dir=tuple(lidar_data['dir']),
      up=tuple(lidar_data['up']),
      vertical_resolution=lidar_data['vertical_resolution'],
      horizontal_angle=lidar_data['horizontal_angle'],
      is_rotate_mode=lidar_data['is_rotate_mode'],
    )
    self.frequency = lidar_data['frequency']
    self.frame = frame
    
  def send(self):
    data_publisher_instance = DataPublisherSingleton()
    vehicle_instance = VehicleSingleton()
    stop_event_instance = StopEventSingleton()
    
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event_instance.get_value():
      data = self.lidar.poll()
      if data is None:
        print("No data received from the Lidar")
        continue
      if 'pointCloud' not in data:
        print("No pointCloud data received from the Lidar")
        continue
      
      pointcloud = data['pointCloud'][::self.DOWNSAMPLE_RATE]
      if len(pointcloud) == 0:
        print("Received empty pointCloud data from the Lidar")
        continue
      
      state = vehicle_instance.get_state()
      if state is None:
        print("No state data received from the Vehicle")
        continue
      
      if self.frame == "base_link":
        position = state["pos"]
        relative_pcd = np.array(pointcloud - position + self.OFFSET, dtype=np.float32)
      else:
        position = self.lidar.get_position()
        relative_pcd = np.array(pointcloud - position, dtype=np.float32)
        
      rotation = R.from_quat(state["rotation"])
      yaw, pitch, roll = rotation.as_euler("xyz", degrees=True) + np.array([90, 0, 0])
      rotation_matrix = R.from_euler("xyz", [roll, pitch, yaw], degrees=True).as_matrix()
      rotated_pcd = np.dot(relative_pcd, rotation_matrix.T)
      
      intensity_column = np.full((len(rotated_pcd), 1), self.INTENSITY)
      pcd_with_intensity = np.concatenate([rotated_pcd, intensity_column], axis=1).astype(np.float32)
      
      data_publisher_instance.lidar(pcd_with_intensity, self.frame)
      
      next_time = max(0, interval - (time.time() - base_time))
      if next_time > 0:
        time.sleep(next_time)
      base_time = time.time()

