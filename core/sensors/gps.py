import time

import numpy as np

from beamngpy.sensors import GPS

from core.singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleSingleton

class GPSManager:
  OFFSET = [0.33022292, -1.26480627, 0.77556159666]
  
  def __init__(self, bng, vehicle, gps_data):
    self.gps = GPS(
      gps_data['nama'],
      bng,
      vehicle,
      pos=tuple(gps_data['pos']),
      ref_lon=gps_data['ref_lon'],
      ref_lat=gps_data['ref_lat'],
      is_visualised=gps_data['is_visualised'],
    )
    self.frequency = gps_data['frequency']
    
  def _find_closest_coordinates(self, gps_data, relative_pos):
    min_x, min_y = float('inf'), float('inf')
    closest_x, closest_y = None, None

    for index, data in gps_data.items():
      dist_x, dist_y = abs(data['x'] - relative_pos[0]), abs(data['y'] - relative_pos[1])
      if dist_x < min_x:
        min_x, closest_x = dist_x, data['x']
      if dist_y < min_y:
        min_y, closest_y = dist_y, data['y']

    return [closest_x, closest_y, relative_pos[2]]

  def send(self):
    data_publisher_instance = DataPublisherSingleton()
    vehicle_instance = VehicleSingleton()
    self.stop_event = StopEventSingleton()
    
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not self.stop_event.get_value():
      state = vehicle_instance.get_state()
      if state is None:
        continue

      relative_pos = np.array(state["pos"], dtype=np.float32) + self.OFFSET
      gps_data = self.gps.poll()

      if gps_data:
        closest_coordinates = self._find_closest_coordinates(gps_data, relative_pos)
        data_publisher_instance.gps(closest_coordinates)

      next_time = max(0, interval - (time.time() - base_time))
      if next_time > 0:
        time.sleep(next_time)
      base_time = time.time()
      
      