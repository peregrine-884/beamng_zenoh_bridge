import zenoh
import time
import random
import numpy as np

from msg.tier4_vehicle_msgs import ActuationCommandStamped
from shared import *

vehicle_instance = VehicleSingleton()
vehicle_state_instance = VehicleStateSingleton()

brake_flag = False
accel_flag = False

# ノイズ設定
accel_std = 0.25
steer_std = 0.1
interval = 10
current_index = 0
flag = True

def model_control_callback(sample: zenoh.Sample):
  global brake_flag, accel_flag, interval, accel_std, steer_std, current_index, flag
  
  current_time = time.time()
  
  if vehicle_state_instance.get_manual_mode():
    return
  
  payload_bytes = bytes(sample.payload)
  payload = bytearray(payload_bytes)
  control_cmd = ActuationCommandStamped.deserialize(payload).actuation
  
  accel = control_cmd.accel_cmd
  brake = control_cmd.brake_cmd
  steer = control_cmd.steer_cmd
  
  # print("Unprocessed")
  # print(f"Throttle: {accel:.3f}, Brake: {brake:.3f}, Steering: {steer:.3f}")
  
  # ノイズを加える
  if flag:
    # accel_noise = np.random.normal(0, accel_std)
    # accel += accel_noise
    
    # steer_noise = np.random.normal(0, steer_std)
    # steer += steer_noise
    
    # print(f"---- Noise {current_index} ----")
    # print(f"Accel: {accel_noise:.3f}")
    # print(f"Steer: {steer_noise:.3f}")
    
    # print(f"Accel: {accel_noise:.3f}, Steer: {steer_noise:.3f}")
    
    if current_index % interval == 0:
      flag = False
  else:
    if current_index % interval == 0:
      flag = True
      
  current_index += 1
  
  # accel
  accel = max(0.0, min(accel, 1.0))
  
  # steer
  # Autowareの出力はタイヤの角度なのでそれを-1~1に変換
  steer = max(-0.7, min(steer, 0.7))
  steer = -1 * (steer / 0.7)
  
  # modelの出力は車両に与える値なのでそのまま使用する
  # steer = max(-1.0, min(steer, 1.0))
  
  # brake
  if accel == 0:
    accel_flag = False
  else:
    accel_flag = True
    
  velocity = vehicle_state_instance.get_longitudinal_vel()
  
  if velocity < 0.0 and not accel_flag:
    brake = 0.0
    
  print("Processed")
  print(f"Throttle: {accel:.3f}, Brake: {brake:.3f}, Steering: {steer:.3f}")
  
  vehicle_instance.set_control(
    steering=steer,
    throttle=accel,
    brake=brake,
  )
  
  # vehicle_instance.set_control(
  #   steering=normalized_steering,
  #   throttle=control_cmd.brake_cmd,
  #   brake=control_cmd.accel_cmd,
  # )