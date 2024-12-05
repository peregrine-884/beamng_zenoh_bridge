import zenoh
import time

from msg.vehicle_control_stamped import VehicleControlStamped
from shared import *

last_time = None
update_interval = 0.05 # 20Hzの更新間隔

vehicle_instance = VehicleSingleton()
vehicle_state_instance = VehicleStateSingleton()

def model_control_callback(sample: zenoh.Sample):
  global last_time
  
  current_time = time.time()
  
  delta_time = 0
  if last_time is not None:
    delta_time = current_time - last_time
    
    if delta_time < update_interval:
      time.sleep(update_interval - delta_time)
      return
    
  last_time = current_time
  
  if vehicle_state_instance.get_manual_mode():
    return
  
  payload_bytes = bytes(sample.payload)
  payload = bytearray(payload_bytes)
  control_cmd = VehicleControlStamped.deserialize(payload)
  
  print(f"Throttle: {control_cmd.throttle}, Brake: {control_cmd.brake}, Steering: {control_cmd.steering}, ")
  
  vehicle_instance.set_control(
    steering=control_cmd.steering,
    throttle=control_cmd.throttle,
    brake=0,
  )