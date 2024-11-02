import zenoh
from PID_Py.PID import PID
import time

from msg.autoware_control_msgs import Control
from shared import *

last_time = None
update_interval = 0.05 # 20Hzの更新間隔
steering_pid = PID(kp = 50.0, ki = 5.0, kd = 0.0, outputLimits = (-100, 100))
throttle_pid = PID(kp = 50.0, ki = 5.0, kd = 0.0, outputLimits = (-100, 100))
vehicle_instance = VehicleSingleton()
vehicle_state_instance = VehicleStateSingleton()

def control_callback(sample: zenoh.Sample):
    global last_time

    current_time = time.time()

    if last_time is not None:
        delta_time = current_time - last_time
        print(f"Delta Time: {delta_time:.4f} seconds")

        if delta_time < update_interval:
            return

    last_time = current_time
    
    if vehicle_state_instance.get_manual_mode():
        return

    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    control_cmd = Control.deserialize(payload)

    # 目標速度(m/s)、ステアリング(rad)
    target_velocity = control_cmd.longitudinal.velocity
    target_steering_tire = control_cmd.lateral.steering_tire_angle

    throttle = throttle_pid(setpoint = target_velocity, processValue = vehicle_state_instance.get_longitudinal_vel())
    steering = steering_pid(setpoint = target_steering_tire, processValue = vehicle_state_instance.get_steering_tire_angle())

    throttle = max(-100, min(throttle, 100))
    throttle_command = throttle / 100.0

    steering = max(-100, min(steering, 100))
    steering_command = -steering / 100.0
        
    if 0 <= throttle_command <= 1:
        brake_command = 0
    else:
        brake_command = -throttle_command  # 負のスロットル値に応じてブレーキを設定
        throttle_command = 0
    
    
    vehicle_instance.set_control(
        steering=steering_command,
        throttle=throttle_command,
        brake=brake_command
    )