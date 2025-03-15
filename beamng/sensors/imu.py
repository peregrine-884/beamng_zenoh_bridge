import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from beamngpy.sensors import AdvancedIMU

from zenoh_bridge import IMUDataPublisher
from beamng.utils.sleep_until_next import sleep_until_next

class ImuManager:
  def __init__(self, bng, vehicle, imu_config, zenoh_config):
    self.imu = AdvancedIMU(
      imu_config['name'],
      bng,
      vehicle,
      gfx_update_time=imu_config['gfx_update_time'],
      pos=tuple(imu_config['pos']),
      dir=tuple(imu_config['dir']),
      up=tuple(imu_config['up']),
      is_send_immediately=imu_config['is_send_immediately'],
      is_using_gravity=imu_config['is_using_gravity'],
      is_visualised=imu_config['is_visualised'],
      is_dir_world_space=imu_config['is_dir_world_space'],
    )
    self.frequency = imu_config['frequency']
    self.frame_id = imu_config['frame_id']

    self.publisher = IMUDataPublisher(zenoh_config, imu_config['topic_name'])
    
    print(f'{imu_config["name"]}: {imu_config["topic_name"]}')
    
  def send(self, stop_event):  
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event.is_set():
      data = self.imu.poll()
      if data is None:
        continue
      
      acc_raw = np.array(data['accRaw'])
      ang_vel = np.array(data['angVel'])
      
      # IMUの回転行列
      rotation_matrix = np.array([data['dirX'], data['dirY'], data['dirZ']]).T
      rotation = R.from_matrix(rotation_matrix)
      
      # オイラー角の補正
      euler_angles = rotation.as_euler('xyz', degrees=True)
      euler_angles[2] += 135
      adjusted_rotation =  R.from_euler('xyz', [euler_angles[0], euler_angles[1], euler_angles[2]], degrees=True)
      adjusted_rotation_matrix = adjusted_rotation.as_matrix()
      
      # IMUデータの座標変換
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
      
      R_combined = R_z @ R_y @ R_x
      acc_local = R_combined @ acc_raw
      
      quaternion = adjusted_rotation.as_quat()
      
      imu_data = quaternion.tolist() + ang_vel.tolist() + acc_local.tolist()

      self.publisher.publish(self.frame_id, imu_data)
      
      # 次の送信まで待機
      base_time = sleep_until_next(interval, base_time)