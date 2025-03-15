import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from beamngpy.sensors import Lidar

from zenoh_bridge import LidarDataPublisher
from beamng.utils.sleep_until_next import sleep_until_next

class LidarManager:
  INTENSITY = 128
  DOWNSAMPLE_RATE = 3
  OFFSET = np.array([0.3302292, 1.653519373, 0.12556159596657])

  def __init__(self, bng, vehicle, vehicle_data, lidar_config, zenoh_config):
    self.lidar = Lidar(
      lidar_config['name'],
      bng,
      vehicle,
      requested_update_time=lidar_config['requested_update_time'],
      pos=tuple(lidar_config['pos']), 
      dir=tuple(lidar_config['dir']),
      up=tuple(lidar_config['up']),
      vertical_resolution=lidar_config['vertical_resolution'],
      horizontal_angle=lidar_config['horizontal_angle'],
      is_rotate_mode=lidar_config['is_rotate_mode'],
      is_360_mode=lidar_config['is_360_mode'],
      is_using_shared_memory=lidar_config['is_using_shared_memory'],
      is_visualised=lidar_config['is_visualised'],
      is_streaming=lidar_config['is_streaming'],
      is_dir_world_space=lidar_config['is_dir_world_space'],
    )
    self.frequency = lidar_config['frequency']
    self.frame_id = lidar_config['frame_id']

    self.publisher = LidarDataPublisher(zenoh_config, lidar_config['topic_name'])
    
    self.vehicle_data = vehicle_data
    
    print(f'{lidar_config["name"]}: {lidar_config["topic_name"]}')
    
  def send(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event.is_set():
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
      
      state = self.vehicle_data.get_state()
      
      if self.frame_id == "base_link":
        position = state["pos"]
        relative_pcd = np.array(pointcloud - position + self.OFFSET, dtype=np.float32)
      else:
        position = self.lidar.get_position()
        relative_pcd = np.array(pointcloud - position, dtype=np.float32)
        
      rotation = state["rotation"]
      r = R.from_quat(rotation)
      yaw = r.as_euler('xyz', degrees=True)[2] + 90
      pitch = r.as_euler('xyz', degrees=True)[1]
      roll = r.as_euler('xyz', degrees=True)[0]
      new_rotation = R.from_euler('xyz', [roll, pitch, yaw], degrees=True)
      rotation_matrix = new_rotation.as_matrix()
      rotated_pcd = np.dot(relative_pcd, rotation_matrix.T)
      
      intensity_column = np.full((len(rotated_pcd), 1), self.INTENSITY)
      pcd_with_intensity = np.concatenate([rotated_pcd, intensity_column], axis=1).astype(np.float32)
      
      self.publisher.publish(self.frame_id, pcd_with_intensity)
      
      base_time = sleep_until_next(interval, base_time)

