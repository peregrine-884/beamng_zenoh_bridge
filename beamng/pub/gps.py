import time
import numpy as np
from singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleSingleton

offset = [0.33022292, -1.26480627, 0.77556159666]

def send_gps(gps):
  data_publisher_instance = DataPublisherSingleton()
  vehicle_instance = VehicleSingleton()
  stop_event_instance = StopEventSingleton()
  
  gps_hz = 10
  gps_interval = 1.0 / gps_hz
  base_time = time.time()
  
  while True:
    if stop_event_instance.get_value():
      break
    
    state = vehicle_instance.get_state()
    if state is None: continue
    pos = state["pos"]
    relative_pos = np.array(pos + offset, dtype=np.float32)
    
    min_distance_x = float('inf')
    min_distance_y = float('inf')
    closest_x = None
    closest_y = None
    data_front = gps.poll()
    if data_front:
      for index, data in data_front.items():
        dist_x = abs(data['x'] - relative_pos[0])
        dist_y = abs(data['y'] - relative_pos[1])
        if dist_x < min_distance_x:
          min_distance_x = dist_x
          closest_x = (index, data['x'])
        if dist_y < min_distance_y:
          min_distance_y = dist_y
          closest_y = (index, data['y'])
          
      gps_data = [
        closest_x[1],
        closest_y[1],
        relative_pos[2]
      ]

      data_publisher_instance.gps(gps_data)
    
    next_time = max(0, gps_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()