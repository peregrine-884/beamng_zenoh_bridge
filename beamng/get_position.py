import numpy as np
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Lidar, Electrics, Camera, AdvancedIMU
import keyboard
import threading
import random
import beamng_publisher
import zenoh

from shared import *

from pub.lidar import send_lidar_data
from pub.imu import send_imu_data
from pub.vehicle_info import send_vehicle_info_data
from pub.clock import send_clock_data
from pub.camera import send_camera_data

from sub.control import control_callback
from sub.hazard_lights import hazard_lights_callback
from sub.turn_indicators import turn_indicators_callback

import time

def main():    
    # beamNG
    random.seed(1703)
    set_up_simple_logging()

    beamng = BeamNGpy('localhost', 64256)
    bng = beamng.open(launch=False)
    
    # scenario = Scenario('2k_tsukuba_s', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
    
    scenario = Scenario('tech_ground', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
    
    vehicle = Vehicle('ego_vehicle', model='etk800', license='RED', color='Blue')
    
    scenario.add_vehicle(vehicle,
        pos=(-1020.482, 0.000, 1.000), rot_quat=(0.0, 0.0, -0.70710678, 0.70710678)
    )
    
    # scenario.add_vehicle(vehicle, pos=(0, 0, 0))
    
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
    
    vehicle.sensors.attach('electrics', Electrics())
    
    while True:
        time.sleep(1)
        
        vehicle.control(steering=0)
        
        position = lidar.get_position()
        print(position)

        if position[0] >= 1050:
            vehicle.teleport(
                pos=(-1020.482, 0.000, 1.000), rot_quat=(0.0, 0.0, -0.70710678, 0.70710678), reset=True
            )
    
    lidar.remove()
    # bng.close()

if __name__ == '__main__':
    
    main()