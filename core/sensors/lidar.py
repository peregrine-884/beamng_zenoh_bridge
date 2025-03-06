import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from beamngpy.sensors import Lidar

from singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleSingleton

class Lidarmanager:
  INTENSITY = 128
  DOWNSAMPLE_RATE = 9
  OFFSET = np.array([0.3302292, 1.653519373, 0.12556159596657])
  LIDAR_HZ = 10

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

