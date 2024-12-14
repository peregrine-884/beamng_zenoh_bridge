import zenoh
import time

from msg.tier4_vehicle_msgs import ActuationCommandStamped
from shared import *

vehicle_instance = VehicleSingleton()
vehicle_state_instance = VehicleStateSingleton()

brake_flag = False
accel_flag = False

def model_control_callback(sample: zenoh.Sample):
  if vehicle_state_instance.get_manual_mode():
    return
  
  payload_bytes = bytes(sample.payload)
  payload = bytearray(payload_bytes)
  control_cmd = ActuationCommandStamped.deserialize(payload).actuation
  
  accel = control_cmd.accel_cmd
  brake = control_cmd.brake_cmd
  steer = control_cmd.steer_cmd
  
  print("Unprocessed")
  print(f"Throttle: {accel:.3f}, Brake: {brake:.3f}, Steering: {steer:.3f}")
  
  # steer
  steer = max(-0.7, min(steer, 0.7))
  steer = -1 * (steer / 0.7)
  
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