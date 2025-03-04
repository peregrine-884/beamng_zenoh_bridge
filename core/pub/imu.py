import numpy as np
from scipy.spatial.transform import Rotation as R
import time

from singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleStateSingleton

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
    angVel = np.array(data['angVel'])
    
    # print('1111')
    
    heading_rate = angVel[2]
    vehicle_state_instance.set_heading_rate(heading_rate)
    
    # print('2222')
    
    dirX = data['dirX']
    dirY = data['dirY']
    dirZ = data['dirZ']
    
    # print('3333')
    
    rotation_matrix = np.array([dirX, dirY, dirZ]).T
    
    # print('4444')
    
    rotation = R.from_matrix(rotation_matrix)
    euler_angles = rotation.as_euler('xyz', degrees=True)
    # euler_angles[0] += 45
    # euler_angles[1] += 0
    euler_angles[2] += 135
    adjusted_rotation = R.from_euler('xyz', [euler_angles[0], euler_angles[1], euler_angles[2]], degrees=True)
    adjusted_rotation_matrix = adjusted_rotation.as_matrix()
    
    # print('5555')
    
    # accLocal = adjusted_rotation_matrix @ accRaw
    # angVelLocal = adjusted_rotation_matrix @ angVel
    
    yaw_angle = np.radians(0)
    pitch_angle = np.radians(0)
    roll_angle = np.radians(-90)

    R_z = np.array([
        [np.cos(yaw_angle), -np.sin(yaw_angle), 0],
        [np.sin(yaw_angle), np.cos(yaw_angle), 0],
        [0, 0, 1]
    ])

    R_y = np.array([
        [np.cos(pitch_angle), 0, np.sin(pitch_angle)],
        [0, 1, 0],
        [-np.sin(pitch_angle), 0, np.cos(pitch_angle)]
    ])

    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll_angle), -np.sin(roll_angle)],
        [0, np.sin(roll_angle), np.cos(roll_angle)]
    ])

    R_combined = R_x @ R_y @ R_z
    accLocal = R_combined @ accRaw

    quaternion = adjusted_rotation.as_quat()
    
    # print('6666')
    
    imu_data = quaternion.tolist() + angVel.tolist() + accLocal.tolist()
    
    # print('7777')
    
    data_publisher_instance.imu(imu_data)
    
    # print('8888')
    
    next_time = max(0, imu_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
    
    # print('9999')
