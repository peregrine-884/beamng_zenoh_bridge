import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleSingleton

INTENSITY = 128
DOWNSAMPLE_RATE = 9
OFFSET = np.array([0.3302292, 1.653519373, 0.12556159596657])
LIDAR_HZ = 10

def send_lidar_data(lidar, frame):
  data_publisher_instance = DataPublisherSingleton()
  vehicle_instance = VehicleSingleton()
  stop_event_instance = StopEventSingleton()
  
  lidar_interval = 1.0 / LIDAR_HZ
  base_time = time.time()

  while not stop_event_instance.get_value():
    data = lidar.poll()
    if data is None or 'pointCloud' not in data:
      continue

    pointcloud = data['pointCloud'][::DOWNSAMPLE_RATE]
    if len(pointcloud) == 0:
      continue

    state = vehicle_instance.get_state()
    if state is None:
      continue

    if frame == "base_link":
      position = state["pos"]
      relative_pcd = np.array(pointcloud - position + OFFSET, dtype=np.float32)
    else:
      position = lidar.get_position()
      relative_pcd = np.array(pointcloud - position, dtype=np.float32)

    rotation = R.from_quat(state["rotation"])
    yaw, pitch, roll = rotation.as_euler("xyz", degrees=True) + np.array([90, 0, 0])
    rotation_matrix = R.from_euler("xyz", [roll, pitch, yaw], degrees=True).as_matrix()
    rotated_pcd = np.dot(relative_pcd, rotation_matrix.T)

    intensity_column = np.full((len(rotated_pcd), 1), INTENSITY)
    pcd_with_intensity = np.concatenate([rotated_pcd, intensity_column], axis=1).astype(np.float32)

    data_publisher_instance.lidar(pcd_with_intensity, frame)

    next_time = max(0, lidar_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
      