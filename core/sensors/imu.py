import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from beamngpy.sensors import AdvancedIMU

from core.singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleStateSingleton

class ImuManager:
  def __init__(self, bng, vehicle, imu_data):
    self.imu = AdvancedIMU(
      imu_data['name'],
      bng,
      vehicle,
      gfx_update_time=imu_data['gfx_update_time'],
      pos=tuple(imu_data['pos']),
      dir=tuple(imu_data['dir']),
      up=tuple(imu_data['up']),
      is_send_immediately=imu_data['is_send_immediately'],
      is_using_gravity=imu_data['is_using_gravity'],
      is_visualised=imu_data['is_visualised'],
      is_dir_world_space=imu_data['is_dir_world_space'],
    )
    self.frequency = imu_data['frequency']
    
def send(self):
  data_publisher = DataPublisherSingleton()
  stop_event = StopEventSingleton()
  vehicle_state = VehicleStateSingleton()
  
  interval = 1.0 / self.frequency
  base_time = time.time()
  
  while not stop_event.get_value():
    data = self.imu.poll()
    if data is None:
      continue
    
    acc_raw = np.array(data['accRaw'])
    ang_vel = np.array(data['angVel'])

    # ヘディングレートを保存
    vehicle_state.set_heading_rate(ang_vel[2])
    
    # IMUの回転行列
    rotation_matrix = np.array([data['dirX'], data['dirY'], data['dirZ']]).T
    rotation = R.from_matrix(rotation_matrix)
    
    # オイラー角の補正
    euler_angles = rotation.as_euler('xyz', degrees=True)
    euler_angles[2] += 135
    adjusted_rotation_matrix = R.from_euler('xyz', euler_angles, degrees=True).as_matrix()
    
    # IMUデータの座標変換
    R_combined = R.from_euler('xyz', [0, 0, -90], degrees=True).as_matrix()
    acc_local = R_combined @ acc_raw
    quaternion = R.from_matrix(R_combined).as_quat()
    
    imu_data = quaternion.tolist() + acc_local.tolist() + ang_vel.tolist()
    data_publisher.imu(imu_data)
    
    # 次の送信まで待機
    next_time = max(0, interval - (time.time() - base_time))
    if next_time > 0:
      time.sleep(next_time)
    base_time = time.time()