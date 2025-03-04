import zenoh
import time

from msg.autoware_control_msgs import Control
from singleton_manager import VehicleStateSingleton, VehicleSingleton

class PIDController:
    def __init__(self, Kp, Ki, Kd, output_min=-1, output_max=1):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.output_min = output_min
        self.output_max = output_max
        self.previous_error = 0
        self.integral = 0
        
    def calculate(self, target, current, dt):
        error = target - current
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        self.previous_error = error
        
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        
        output = max(self.output_min, min(self.output_max, output))
        
        return output
    
throttle_pid = PIDController(Kp = 20, Ki = 0.0, Kd = 0.0)

last_time = None
# update_interval = 0.05 # 20Hzの更新間隔

vehicle_instance = VehicleSingleton()
vehicle_state_instance = VehicleStateSingleton()

def control_callback(sample: zenoh.Sample):
    print("--------------------------------------- control_callback")
    global last_time

    current_time = time.time()

    delta_time = 0
    if last_time is not None:
        delta_time = current_time - last_time

        # if delta_time < update_interval:
        #     time.sleep(update_interval - delta_time)
        #     return

    last_time = current_time
    
    if vehicle_state_instance.get_manual_mode():
        return

    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    control_cmd = Control.deserialize(payload)
    
    # steering
    steering = control_cmd.lateral.steering_tire_angle
    steering = max(-0.7, min(steering, 0.7))
    normalized_steering = -1 * (steering / 0.7)
    
    # throttle, brake
    target_velocity = control_cmd.longitudinal.velocity
    current_speed = vehicle_state_instance.get_longitudinal_vel()
    throttle = throttle_pid.calculate(
        target=target_velocity,
        current=current_speed,
        dt=delta_time
    )
    
    # print(target_velocity)
    
    if throttle >= 0:
        throttle_command = throttle
        brake_command = 0
    else:
        throttle_command = 0
        brake_command = -throttle
    
    vehicle_instance.set_control(
        steering=normalized_steering,
        throttle=throttle_command,
        brake=0
    )