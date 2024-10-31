from enum import Enum
from typing import List
import numpy as np
from datetime import datetime
import time
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Lidar, Electrics, Camera, AdvancedIMU
import keyboard
import threading
import random
import lidar_serializer
from scipy.spatial.transform import Rotation as R

import zenoh
from pycdr2 import IdlStruct
from pycdr2.types import uint8, uint32, int32, float32
from dataclasses import dataclass

@dataclass
class Time(IdlStruct, typename="Time"):
    sec: int32
    nanosec: uint32
    
@dataclass
class Lateral(IdlStruct, typename="Lateral"):
    stamp: Time
    control_time: Time
    steering_tire_angle: float32
    steering_tire_rotation_rate: float32
    is_defined_steering_tire_rotation_rate: bool

@dataclass
class Longitudinal(IdlStruct, typename="Longitudinal"):
    stamp: Time
    control_time: Time
    velocity: float32
    acceleration: float32
    jerk: float32
    is_defined_acceleration: bool
    is_defined_jerk: bool
    
@dataclass
class Control(IdlStruct, typename="Control"):
    stamp: Time
    control_time: Time
    lateral: Lateral
    longitudinal: Longitudinal
    
@dataclass
class TurnIndicatorsCommand(IdlStruct, typename="TurnIndicatorsCommand"):
    stamp: Time
    command: uint8
    
@dataclass
class HazardLightsCommand(IdlStruct, typename="HazardLightsCommand"):
    stamp: Time
    command: uint8

lidar_publisher = lidar_serializer.LidarPublisher()
stop_event = threading.Event()
manual_mode = False
heading_rate = 0.0
offset = np.array([0.3302292, 1.653519373, 0.12556159596657])
downsample_rate = 3

global vehicle

def pub_clock():
    clock_hz = 100
    clock_interval = 1.0 / clock_hz
    base_time = time.time()
    
    while True:
        # start_time = time.time()
        if stop_event.is_set():
            break
        
        lidar_publisher.publish_clock()
        
        next_time = max(0, clock_interval - (time.time() - base_time))
        time.sleep(next_time)
        base_time = time.time()
        
        # diff_time = base_time - start_timeqqqqqq
        # fq = 1.0 / diff_time if diff_time > 0 else 0
        # print(f'Clock Frequency: {fq} Hz')

def get_lidar_data(lidar, vehicle):
    lidar_hz = 10
    lidar_interval = 1.0 / lidar_hz
    base_time = time.time()
    
    while True:
        # start_time = time.time()
        if stop_event.is_set():
            break
        
        # start_get_data = time.time()
        data = lidar.poll()
        # end_get_data = time.time()
        # get_data_time = end_get_data - start_get_data
        # get_data_hz = 1.0 / get_data_time if get_data_time > 0 else 0
        # print(f'get_data: {get_data_hz}: Hz')
        
        pointcloud = data['pointCloud'][::downsample_rate]
        num_points = pointcloud.shape[0]
        
        if pointcloud is not None and len(pointcloud) > 0: 
            # start_process_data = time.time()
            vehicle.sensors.poll()
            position = vehicle.sensors["state"]["pos"]
            relative_pointcloud = np.array(pointcloud - position + offset, dtype=np.float32)
            
            # position = lidar.get_position()
            # relative_pointcloud = np.array(pointcloud - position, dtype=np.float32)
            
            rotation = vehicle.sensors["state"]["rotation"]
            r = R.from_quat(rotation)
            yaw = r.as_euler('xyz', degrees=True)[2] + 90
            pitch = r.as_euler('xyz', degrees=True)[1]
            roll = r.as_euler('xyz', degrees=True)[0]
            new_rotation = R.from_euler('xyz', [roll, pitch, yaw], degrees=True)
            rotation_matrix = new_rotation.as_matrix()
            rotated_pointcloud = np.dot(relative_pointcloud, rotation_matrix.T)
            
            intensity = 128
            new_column_intensity = np.full((num_points, 1), intensity)
            
            pointcloud_4d = np.concatenate([rotated_pointcloud, new_column_intensity], axis=1).astype(np.float32)
            
            # end_process_data = time.time()
            # process_data_time = end_process_data - start_process_data
            # process_data_hz = 1.0 / process_data_time if process_data_time > 0 else 0
            # print(f'process_data: {process_data_hz}: Hz')
            
            # start_pub_data = time.time()
            
            lidar_publisher.process_pointcloud(pointcloud_4d)
            
            # end_pub_data = time.time()
            # pub_data_time = end_pub_data - start_pub_data
            # pub_data_hz = 1.0 / pub_data_time if pub_data_time > 0 else 0
            # print(f'pub_data: {pub_data_hz}: Hz')
            
            # current_time = time.time()
            # time_column = np.full((num_points, 1), current_time)
            
            # pointcloud_5d = np.concatenate([rotated_pointcloud, new_column_intensity, time_column], axis=1).astype(np.float32)
        
            # lidar_publisher.process_pointcloud(pointcloud_5d)
            
        next_time = max(0, lidar_interval - (time.time() - base_time))
        time.sleep(next_time)
        base_time = time.time()
        
        # diff_time = base_time - start_time
        # fq = 1.0 / diff_time if diff_time > 0 else 0
        # print(f'LiDAR Frequency: {fq} Hz')
        
def get_camera_data(camera):
    camera_hz = 30
    camera_interval = 1.0 / camera_hz
    base_time = time.time()
    
    while True:
        if stop_event.is_set():
            break
        
        data = camera.stream_raw()
        image_data = data['colour'].tobytes()
        
        lidar_publisher.process_camera(image_data)
        
        next_time = max(0, camera_interval - (time.time() - base_time))
        time.sleep(next_time)
        base_time = time.time()
        
def get_imu_data(imu):
    imu_hz = 25
    imu_interval = 1.0 / imu_hz
    base_time = time.time()
    
    while True:
        # start_time = time.time()
        if stop_event.is_set():
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

        quaternion = adjusted_rotation.as_quat()
        
        imu_data = quaternion.tolist() + angVelLocal.tolist() + accLocal.tolist()
        
        lidar_publisher.process_imu(imu_data)
        
        next_time = max(0, imu_interval - (time.time() - base_time))
        time.sleep(next_time)
        base_time = time.time()
        
        # diff_time = base_time - start_time
        # fq = 1.0 / diff_time if diff_time > 0 else 0
        # print(f'IMU Frequency: {fq} Hz')
        
def get_vehicle_data(vehicle):
    vehicle_hz = 10
    vehicle_interval = 1.0 / vehicle_hz
    base_time = time.time()
    
    while True:
        # start = time.time()
        if stop_event.is_set():
            break
        
        vehicle.sensors.poll()
        state = vehicle.sensors['state']
        electrics = vehicle.sensors['electrics']
        
        # velocity m/s
        dir = state['dir']
        vel = state['vel']
        
        dir_norm = dir / np.linalg.norm(dir)
        longitudinal_vel = np.dot(vel, dir_norm)
        
        lateral_dir = np.array([-dir_norm[1], dir_norm[0], 0])
        lateral_vel = np.dot(vel, lateral_dir)
        
        # steering 
        # left(positive) right(negative) center(0.0)
        # 車両の最大操舵角を0.7[rad]に設定する
        steering_input = electrics['steering_input']
        steering_tire_angle = steering_input * 0.7
        
        # gear
        gear = electrics['gear']
        if gear == 'N':
            gear_value = 1
        elif gear == 'R':
            gear_value = 20
        elif gear == 'D':
            gear_value = 2
        else:
            gear_value = 0
        
        # control_mode
        control_mode = 4 if manual_mode else 1
        
        # battery
        fuel = electrics['fuel'] * 100
        
        # hazard_light
        hazard_signal = electrics['hazard_signal']
        hazard_report = 2 if hazard_signal else 1
        
        # turn_indicators
        turn_signal = electrics['turnsignal']
        if turn_signal > 0.1:
            turn_report = 3
        elif turn_signal < -0.1:
            turn_report = 2
        else:
            turn_report = 1
            
        vehicle_status = [
            longitudinal_vel,
            lateral_vel,
            heading_rate,
            steering_tire_angle,
            gear_value,
            control_mode,
            fuel,
            hazard_report,
            turn_report
        ]
        
        lidar_publisher.process_vehicle_status(*vehicle_status)
        
        next_time = max(0, vehicle_interval - (time.time() - base_time))
        time.sleep(next_time)
        base_time = time.time()
        
        # diff_time = base_time - start
        # fq = 1.0 / diff_time if diff_time > 0 else 0
        # print(f'Vehicle Frequency: {fq} Hz')
        
def toggle_control_mode(event):
    global manual_mode
    manual_mode = not manual_mode

last_time_received = None
def control_callback(sample: zenoh.Sample):
    global last_time_received

    # sample.payloadをbytesに変換してデシリアライズ
    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    control_cmd = Control.deserialize(payload)
    
    # current_time = time.time()
    
    # if last_time_received is not None:
    #     time_diff = current_time - last_time_received
    #     frequency = 1 / time_diff if time_diff > 0 else float('inf')
    #     print(f'Received at {frequency:.2f} Hz')
        
    # last_time_received = current_time
    
    # print("Control Command Data:")
    # print(f"Stamp: {control_cmd.stamp}")
    # print(f"Control Time: {control_cmd.control_time}")
    
    # # Lateral control data
    # print("Lateral Control:")
    # print(f"  Steering Tire Angle: {control_cmd.lateral.steering_tire_angle}")
    # print(f"  Steering Tire Rotation Rate: {control_cmd.lateral.steering_tire_rotation_rate}")
    # print(f"  Defined Steering Tire Rotation Rate: {control_cmd.lateral.is_defined_steering_tire_rotation_rate}")
    
    # # Longitudinal control data
    # print("Longitudinal Control:")
    # print(f"  Velocity: {control_cmd.longitudinal.velocity}")
    # print(f"  Acceleration: {control_cmd.longitudinal.acceleration}")
    # print(f"  Jerk: {control_cmd.longitudinal.jerk}")
    # print(f"  Defined Acceleration: {control_cmd.longitudinal.is_defined_acceleration}")
    # print(f"  Defined Jerk: {control_cmd.longitudinal.is_defined_jerk}")
        
        
enable_left = False
enable_right = False
enable_hazard_lights = False
def turn_indicators_callback(sample: zenoh.Sample):
    global enable_left, enable_right, enable_hazard_lights, vehicle
    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    turn_indicators_cmd = TurnIndicatorsCommand.deserialize(payload).command
    
    if turn_indicators_cmd == 1:
        enable_left = False
        enable_right = False
    elif turn_indicators_cmd == 2:
        enable_left = True
    elif turn_indicators_cmd == 3:
        enable_right = True
        
    if not (turn_indicators_cmd == 0):
        vehicle.set_lights(
            left_signal=enable_left,
            right_signal=enable_right,
            hazard_signal=enable_hazard_lights
        )
    
def hazard_lights_callback(sample: zenoh.Sample):
    global enable_left, enable_right, enable_hazard_lights, vehicle
    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    hazard_lights_cmd = HazardLightsCommand.deserialize(payload).command
    
    if hazard_lights_cmd == 1:
        enable_hazard_lights = False
    elif hazard_lights_cmd == 2:
        enable_hazard_lights = True
        
    if not (hazard_lights_cmd == 0):
        vehicle.set_lights(
            left_signal=enable_left,
            right_signal=enable_right,
            hazard_signal=enable_hazard_lights
        )

def main():
    global vehicle
    # zenohの設定
    config = zenoh.Config.from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
    session = zenoh.open(config)
    key = 'control/command/control_cmd'
    control_sub = session.declare_subscriber(key, control_callback)
    
    key = 'control/command/turn_indicators_cmd'
    turn_indicators_sub = session.declare_subscriber(key, turn_indicators_callback)
    
    key = 'control/command/hazard_lights_cmd'
    hazard_lights_sub = session.declare_subscriber(key, hazard_lights_callback)
    
    # beamNGの設定
    random.seed(1703)
    set_up_simple_logging()
    
    beamng = BeamNGpy('localhost', 64256)
    bng = beamng.open(launch=False)
    
    scenario = Scenario('west_coast_usa', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
    
    vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
    
    scenario.add_vehicle(vehicle,
        pos=(-717.121, 101, 118.675), rot_quat=(0, 0, 0.3826834, 0.9238795)
    )
    
    scenario.make(bng)
    
    bng.settings.set_deterministic(60)
    bng.scenario.load(scenario)
    bng.ui.hide_hud()
    bng.scenario.start()
    
    # Lidar
    lidar = Lidar(
        'lidar1',
        bng,
        vehicle,
        requested_update_time=0.01,
        pos=(0, 0.65, 2.0),
        dir=(0, -1, 0),
        up=(0, 0, 1),
        vertical_resolution=32,
        horizontal_angle=360,
        is_rotate_mode=False,
        is_360_mode=True,
        is_using_shared_memory=True,
        is_visualised=False,
        is_streaming=True,
        is_dir_world_space=False
    )
    
    # Camera
    # camera = Camera(
    #     'camera1',
    #     bng,
    #     vehicle,
    #     requested_update_time=0.01,
    #     pos=(0, 0, 3),
    #     dir=(0, -1, 0),
    #     up=(0, 0, 1),
    #     resolution=(640, 480),
    #     near_far_planes=(0.05, 150),
    #     is_using_shared_memory=True,
    #     is_render_annotations=False,
    #     is_render_instance=False,
    #     is_render_depth=False,
    #     is_visualised=False,
    #     is_streaming=True,
    #     is_dir_world_space=False
    # )
    
    # IMU
    imu = AdvancedIMU(
        'imu',
        bng,
        vehicle,
        gfx_update_time=0.005,
        pos=(0, 0.5, 0.45),
        dir=(0, -1, 0),
        up=(-0, 0, 1),
        is_send_immediately=True,
        is_using_gravity=True,
        is_visualised=True,
        is_dir_world_space=False,
    )
    
    # 車両の制御情報
    vehicle.sensors.attach('electrics', Electrics())
    
    # vehicle.set_lights(
    #     left_signal=True,
    #     right_signal=False,
    #     hazard_signal=False
    # )
    
    # vehicle.control(
    #     steering=0.0,
    #     throttle=1.0
    # )
    
    # vehicle.set_velocity(
    #     velocity=3.0,
    #     dt=1.0
    # )
    
    stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
    stop_thread.start()
    
    keyboard.on_press_key('p', toggle_control_mode)
    
    vehicle_thread = threading.Thread(target=get_vehicle_data, args=(vehicle,))
    vehicle_thread.start()
    
    lidar_thread = threading.Thread(target=get_lidar_data, args=(lidar, vehicle))
    lidar_thread.start()
    
    # camera_thread = threading.Thread(target=get_camera_data, args=(camera,))
    # camera_thread.start()
    
    imu_thread = threading.Thread(target=get_imu_data, args=(imu,))
    imu_thread.start()
    
    clock_thread = threading.Thread(target=pub_clock)
    clock_thread.start()
    
    vehicle_thread.join()
    lidar_thread.join()
    # camera_thread.join()
    imu_thread.join()
    clock_thread.join()
    
    lidar.remove()
    # camera.remove()
    imu.remove()
    # bng.close()
    
    control_sub.undeclare()
    turn_indicators_sub.undeclare()
    hazard_lights_sub.undeclare()
    session.close()

if __name__ == '__main__':
    
    main()
