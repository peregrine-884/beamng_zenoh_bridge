import numpy as np
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Lidar, Electrics, Camera, AdvancedIMU, GPS
import keyboard
import threading
import random
import zenoh_bridge
import zenoh
import time
import argparse

from singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleStateSingleton, VehicleSingleton
from pub import send_camera_data, send_clock_data, send_imu_data, send_lidar_data, send_vehicle_control_data, send_vehicle_info_data
from sub import model_control_callback

def get_sensor_data():
  stop_event_instance = StopEventSingleton()
  vehicle_instance = VehicleSingleton()
  
  frequency = 10
  interval = 1.0 / frequency
  base_time = time.time()
  
  while True:
    if stop_event_instance.get_value():
      break

    vehicle_instance.get_sensor_data()

    next_time = max(0, interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()

def main():    
    # beamNG
    random.seed(1703)
    set_up_simple_logging()

    beamng = BeamNGpy('localhost', 64256)
    bng = beamng.open(launch=False)
    
    scenario = Scenario('c1', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
    vehicle = Vehicle('ego_vehicle', model='etk800', license='BLUE', color='Blue')
    vehicle2 = Vehicle('object', model='etk800', license='RED', color='RED')
    vehicle3 = Vehicle('object2', model='etk800', license='RED', color='GREEN')
    
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", type=int)
    parser.add_argument("time_zeno", type=str)
    args = parser.parse_args()
    
    scenario_number = args.scenario
    time_zeno = args.time_zeno
    
    use_vehicle2 = False

    if scenario_number == 1:
        scenario.add_vehicle(vehicle,
            pos=(-5955.8, -13987.0, 897.8), rot_quat=(0.0, 0.0, -0.91706007, 0.39874907)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(-6128.96240234375, -13860.3359375, 879.3995971679688), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 2:
        scenario.add_vehicle(vehicle,
            pos=(-6669.6, -11178.0, 877.3), rot_quat=(0.0, 0.0, 0.97236992, 0.23344536)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(-6420.4150390625, -10880.1279296875, 862.5100708007812), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 3:
        scenario.add_vehicle(vehicle,
            pos=(2713.837890625, 9197.7900390625, 863.1), rot_quat=(0.0, 0.0, -0.76604444, 0.64278761)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(2934.195556640625, 9036.888671875, 869.6454467773438), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 4:
        scenario.add_vehicle(vehicle,
            pos=(5109.5, 7935.5, 862.8), rot_quat=(0.0, 0.0, -0.62932039, 0.77714596)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(5456.4697265625, 7222.41015625, 864.9501342773438), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 5:
        scenario.add_vehicle(vehicle,
            pos=(5398.7, 7642.2, 876.4), rot_quat=(0.0, 0.0, -0.99813480, 0.06104854)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(5140.5087890625, 7927.6982421875, 874.3831176757812), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 6:
        scenario.add_vehicle(vehicle,
            pos=(3794.3, 8799.8, 869.8), rot_quat=(0.0, 0.0, 0.96126170, 0.27563736)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(2960.250732421875, 9072.095703125, 869.6416625976562), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 7:
        scenario.add_vehicle(vehicle,
            pos=(-736.0, 6567.0, 883.4), rot_quat=(0.0, 0.0, 0.28401534, 0.95881973)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(-780.5479125976562, 6180.248046875, 875.3951416015625), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 8:
        scenario.add_vehicle(vehicle,
            pos=(92.8, 5825.8, 861.6), rot_quat=(0.0, 0.0, -0.30070580, 0.95371695)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(602.9493408203125, 5785.6044921875, 862.8590087890625), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 9:
        scenario.add_vehicle(vehicle,
            pos=(-1715.0, -11818.5, 854.8), rot_quat=(0.0, 0.0, 0.52621392, 0.85035222)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(-2559.671630859375, -12235.865234375, 866.0284423828125), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 10:
        scenario.add_vehicle(vehicle,
            pos=(-7072.3, -16158.3, 886.0), rot_quat=(0.0, 0.0, -0.04361939, 0.99904822)
        )
        if use_vehicle2:
            scenario.add_vehicle(vehicle2,
                pos=(-7430.0341796875, -16525.9765625, 865.1105346679688), rot_quat=(0.0, 0.0, 0.0, 1.0)
            )
    elif scenario_number == 100:
        scenario.add_vehicle(vehicle,
            pos=(-1633.80810546875, -11778.748046875, 855.0), rot_quat=(0.0, 0.0, 0.52621392, 0.85035222)
        )
        
        scenario.add_vehicle(vehicle2,
            pos=(-1710.229736328125, -11820.5556640625, 856.0), rot_quat=(0.0, 0.0, 0.52621392, 0.85035222)
        )
        scenario.add_vehicle(vehicle3,
            pos=((-1771.5086669921875, -11850.5615234375, 855.5)), rot_quat=(0.0, 0.0, 0.52621392, 0.85035222)
        )
    elif scenario_number == 200:
        scenario = Scenario('2k_tsukuba', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
        scenario.add_vehicle(vehicle,
            pos=(-96.2, -304.7, 73.7), rot_quat=(0.0, 0.0, 0.35836795, 0.93358043)
        )
        vehicle2 = Vehicle('ego_vehicle2', model='etk800', license='RED', color='Red')
        scenario.add_vehicle(vehicle2,
            pos=(-104.04, -305.19, 74.5), rot_quat=(0.0, 0.0, 0.35836795, 0.93358043)
        )
    elif scenario_number == 201:
        scenario = Scenario('2k_tsukuba_s', 'LiDAR_demo', description='Spanning the map with a LiDAR sensor')
        scenario.add_vehicle(vehicle,
            pos=(-96.2, -304.7, 73.7), rot_quat=(0.0, 0.0, 0.35836795, 0.93358043)
        )
        vehicle2 = Vehicle('ego_vehicle2', model='etk800', license='RED', color='Red')
        scenario.add_vehicle(vehicle2,
            pos=(-104.04, -305.19, 74.5), rot_quat=(0.0, 0.0, 0.35836795, 0.93358043)
        )

    
    scenario.make(bng)
    
    bng.settings.set_deterministic(60)
    bng.scenario.load(scenario)
    bng.ui.hide_hud()
    bng.scenario.start()
    
    if time_zeno== "night":
        bng.env.set_tod(tod=0.0)
        vehicle.set_lights(headlights=2)
    
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
    
    # ref_lon, ref_lat = 0.0, 0.0
    # gps_front = GPS(
    #     "front",
    #     bng,
    #     vehicle,
    #     pos=(0, -1.5, 1.0),
    #     ref_lon=ref_lon,
    #     ref_lat=ref_lat,
    #     is_visualised=True,
    # )
        
    vehicle.sensors.attach('electrics', Electrics())
    
    # vehicle.control(gear=2)
    
    # zenoh
    config = zenoh.Config.from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
    session = zenoh.open(config)
    # key = 'control/command/control_cmd'
    # key = 'rate_limitted/control/command/control_cmd'
    # control_sub = session.declare_subscriber(key, control_callback)
    
    # key = 'control/command/turn_indicators_cmd'
    # turn_indicators_sub = session.declare_subscriber(key, turn_indicators_callback)
    
    # key = 'control/command/hazard_lights_cmd'
    # hazard_lights_sub = session.declare_subscriber(key, hazard_lights_callback)
    
    key = 'rate_limitted/control/command/actuation_cmd'
    # key = 'model/rate_limitted/vehicle/command/actuation_cmd'
    model_vehicle_control_sub = session.declare_subscriber(key, model_control_callback)
    
    stop_event = threading.Event()
    stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
    
    data_publisher_instance = DataPublisherSingleton()
    data_publisher_instance.set_data_publisher(zenoh_bridge.BeamngDataPublisher())
    
    vehicle_instance = VehicleSingleton()
    vehicle_instance.set_vehicle(vehicle)
    
    stop_event_instance = StopEventSingleton()
    stop_event_instance.set_stop_event(stop_event)
    
    vehicle_state_instance = VehicleStateSingleton()
    
    keyboard.on_press_key('s', 
        lambda event: vehicle_state_instance.set_manual_mode(not vehicle_state_instance.get_manual_mode()))
    
    camera_thread = threading.Thread(target=send_camera_data, args=(camera,))
    clock_thread = threading.Thread(target=send_clock_data)
    imu_thread = threading.Thread(target=send_imu_data, args=(imu,))
    lidar_thread = threading.Thread(target=send_lidar_data, args=(lidar, "base_link"))
    vehicle_control_thread = threading.Thread(target=send_vehicle_control_data)
    vehicle_info_thread = threading.Thread(target=send_vehicle_info_data)
    get_vehicle_data_thread = threading.Thread(target=get_sensor_data)
    # gps_thread = threading.Thread(target=send_gps, args=(gps_front,))

    stop_thread.start()
    camera_thread.start()
    clock_thread.start()
    imu_thread.start()
    lidar_thread.start()
    vehicle_control_thread.start()
    vehicle_info_thread.start()
    get_vehicle_data_thread.start()
    # gps_thread.start()
    
    threads = [
        stop_thread,
        camera_thread,
        clock_thread,
        imu_thread,
        lidar_thread,
        vehicle_control_thread,
        vehicle_info_thread,
        get_vehicle_data_thread,
        # gps_thread
    ]
    while any(thread.is_alive() for thread in threads):
        # print(", ".join(f"{thread.name} {'is running' if thread.is_alive() else 'has finished'}" for thread in threads))
        position = lidar.get_position()
        print(position)
        
        time.sleep(1)
    
    stop_thread.join()
    camera_thread.join()
    clock_thread.join()
    imu_thread.join()
    lidar_thread.join()
    vehicle_control_thread.join()
    vehicle_info_thread.join()
    get_vehicle_data_thread.join()
    # gps_thread.join()
    
    lidar.remove()
    imu.remove()
    camera.remove()
    # gps_front.remove()
    # bng.close()
    
    # control_sub.undeclare()
    # turn_indicators_sub.undeclare()
    # hazard_lights_sub.undeclare()
    model_vehicle_control_sub.undeclare()
    session.close()

if __name__ == '__main__':
    main()