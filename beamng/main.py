import numpy as np
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Lidar, Electrics, Camera, AdvancedIMU
import keyboard
import threading
import random
import beamng_publisher
import zenoh
import time

from shared import *

from pub.lidar import send_lidar_data
from pub.imu import send_imu_data
from pub.vehicle_info import send_vehicle_info_data
from pub.clock import send_clock_data

from sub.control import control_callback
from sub.hazard_lights import hazard_lights_callback
from sub.turn_indicators import turn_indicators_callback

def main():    
    # beamNG
    random.seed(1703)
    set_up_simple_logging()

    beamng = BeamNGpy('localhost', 64256)
    bng = beamng.open(launch=False)
    
    scenario = Scenario('west_coast_usa', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
    
    vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
    
    scenario.add_vehicle(vehicle,
        pos=(-717.121, 101, 118.675), rot_quat=(0, 0, 0.3826834, 0.9238795)
    )
    
    # scenario = Scenario('2k_tsukuba', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
    # vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
    # scenario.add_vehicle(vehicle,
    #         pos=(-97.2, -304.2, 74.0), rot_quat=(0,0,0.3826834,0.9238795)
    # )
    
    scenario.make(bng)
    
    bng.settings.set_deterministic(60)
    bng.scenario.load(scenario)
    bng.ui.hide_hud()
    bng.scenario.start()
    
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
    
    camera = Camera(
        'camera1',
        bng,
        vehicle,
        requested_update_time=0.01,
        pos=(0, 0, 3),
        dir=(0, -1, 0),
        up=(0, 0, 1),
        resolution=(640, 480),
        near_far_planes=(0.05, 300),
        is_using_shared_memory=True,
        is_render_annotations=False,
        is_render_instance=False,
        is_render_depth=False,
        is_visualised=False,
        is_streaming=True,
        is_dir_world_space=False
    )
    
    vehicle.sensors.attach('electrics', Electrics())
    
    # zenoh
    config = zenoh.Config.from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
    session = zenoh.open(config)
    key = 'control/command/control_cmd'
    control_sub = session.declare_subscriber(key, control_callback)
    
    key = 'control/command/turn_indicators_cmd'
    turn_indicators_sub = session.declare_subscriber(key, turn_indicators_callback)
    
    key = 'control/command/hazard_lights_cmd'
    hazard_lights_sub = session.declare_subscriber(key, hazard_lights_callback)
    
    stop_event = threading.Event()
    stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
    
    data_publisher_instance = DataPublisherSingleton()
    data_publisher_instance.set_data_publisher(beamng_publisher.BeamngPublisher())
    
    vehicle_instance = VehicleSingleton()
    vehicle_instance.set_vehicle(vehicle)
    
    stop_event_instance = StopEventSingleton()
    stop_event_instance.set_stop_event(stop_event)
    
    vehicle_state_instance = VehicleStateSingleton()
    
    keyboard.on_press_key('p', 
        lambda event: vehicle_state_instance.set_manual_mode(not vehicle_state_instance.get_manual_mode()))
    
    lidar_thread = threading.Thread(target=send_lidar_data, args=(lidar,))
    imu_thread = threading.Thread(target=send_imu_data, args=(imu,))
    vehicle_info_thread = threading.Thread(target=send_vehicle_info_data)
    clock_thread = threading.Thread(target=send_clock_data)
    # camera_thread = threading.Thread(target=send_camera_data, args=(camera,))

    stop_thread.start()
    lidar_thread.start()
    imu_thread.start()
    vehicle_info_thread.start()
    clock_thread.start()
    # camera_thread.start()
    
    # threads = [stop_thread, lidar_thread, imu_thread, vehicle_info_thread, clock_thread]
    # threads = [clock_thread, lidar_thread]
    # while any(thread.is_alive() for thread in threads):
    #     for thread in threads:
    #         if thread.is_alive():
    #             print(f"{thread.name} is running.")
    #         else:
    #             print(f"{thread.name} has finished.")
    #     time.sleep(1)
    
    stop_thread.join()
    lidar_thread.join()
    imu_thread.join()
    vehicle_info_thread.join()
    clock_thread.join()
    
    lidar.remove()
    imu.remove()
    camera.remove()
    # bng.close()
    
    control_sub.undeclare()
    turn_indicators_sub.undeclare()
    hazard_lights_sub.undeclare()
    session.close()

if __name__ == '__main__':
    
    main()