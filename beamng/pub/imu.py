import numpy as np
from scipy.spatial.transform import Rotation as R
import time

from shared import *

def send_imu_data(imu):
  data_publisher_instance = DataPublisherSingleton()
  stop_event_instance = StopEventSingleton()
  vehicle_state_instance = VehicleStateSingleton()
  
  imu_hz = 25
  imu_interval = 1.0 / imu_hz
  base_time = time.time()
  
  while True:
    if stop_event_instance.get_value():
      break
    
    data = imu.poll()
    
    accRaw = np.array(data['accRaw'])
    accVel = np.array(data['angVel'])
    
    dirX = data['dirX']
    dirY = data['dirY']
    dirZ = data['dirZ']
    
    rotation_matrix = np.array([dirX, dirY, dirZ]).T
    
    rotation = R.from_matrix(rotation_matrix)
    euler_angles = rotation.as_euler('xyz', degrees=True)
    euler_angles[2] += 90
    adjusted_rotation = R.from_euler('xyz', euler_angles, degrees=True)
    adjusted_rotation_matrix = adjusted_rotation.as_matrix()
    
    accLocal = adjusted_rotation_matrix @ accRaw
    angVelLocal = adjusted_rotation_matrix @ accVel
    heading_rate = angVelLocal[2]
    vehicle_state_instance.set_heading_rate(heading_rate)

    quaternion = adjusted_rotation.as_quat()
    
    imu_data = quaternion.tolist() + angVelLocal.tolist() + accLocal.tolist()
    
    data_publisher_instance.imu(imu_data)
    
    next_time = max(0, imu_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
    
    