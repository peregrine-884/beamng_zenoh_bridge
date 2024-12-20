import random
from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Lidar, Electrics, Camera, AdvancedIMU, GPS
from time import sleep
import keyboard
import threading
import numpy as np

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
  
  scenario.make(bng)
  
  bng.settings.set_deterministic(60)
  bng.scenario.load(scenario)
  bng.ui.hide_hud()
  bng.scenario.start()
  
  ref_lon, ref_lat = 0.0, 0.0
  gps_front = GPS(
    "front",
    bng,
    vehicle,
    pos=(0, -1.5, 1.0),
    ref_lon=ref_lon,
    ref_lat=ref_lat,
    is_visualised=True,
  )
  
  lidar = Lidar(
        'lidar1',
        bng,
        vehicle,
        requested_update_time=0.01,
        pos=(0.0, 0.0, 0.0),
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
  
  camera = Camera(
        'camera1',
        bng,
        vehicle,
        requested_update_time=0.01,
        pos=(0, 0, 0),
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
  
  stop_event = threading.Event()
  stop_thread = threading.Thread(target=lambda: keyboard.wait('q') or stop_event.set())
  stop_thread.start()
  
  offset2 = [0.33022292, -1.26480627, 0.77556159666]
  
  while True:
    if stop_event.is_set():
      break
    
    vehicle.sensors.poll()
    state = vehicle.sensors['state']
    pos = state['pos']
    relative = [pos[0] + offset2[0], pos[1] + offset2[1], pos[2] + offset2[2]]
    rounded = [round(coord, 3) for coord in relative]
    print(f"Vehicle Position x: {rounded[0]:.3f}, y: {rounded[1]:.3f}, z: {rounded[2]:.3f}")
    
    min_distance_x = float('inf')
    min_distance_y = float('inf')
    closest_x = None
    closest_y = None
    data_front = gps_front.poll()
    if data_front:
      for index, data in data_front.items():
        dist_x = abs(data['x'] - rounded[0])
        dist_y = abs(data['y'] - rounded[1])
        if dist_x < min_distance_x:
          min_distance_x = dist_x
          closest_x = (index, data['x'])
        if dist_y < min_distance_y:
          min_distance_y = dist_y
          closest_y = (index, data['y'])
      
      print(f"Closest x: Index: {closest_x[0]}, x: {closest_x[1]:.3f}")
      print(f"Closest y: Index: {closest_y[0]}, y: {closest_y[1]:.3f}")
    
    print("-----")
    
    sleep(1.0)
    
  lidar.remove()
  camera.remove()
  gps_front.remove()
  
if __name__ == '__main__':
  main()