import time

import numpy as np

from beamngpy.sensors import GPS

from zenoh_bridge import GPSDataPublisher
from core.utils.sleep_until_next import sleep_until_next

class GPSManager:
  OFFSET = [0.33022292, -1.26480627, 0.77556159666]
  
  def __init__(self, bng, vehicle, gps_data, config_path):
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

    self.publisher = GPSDataPublisher(config_path, gps_data['topic_name'])
    
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

  def send(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      state = vehicle_instance.get_state()
      if state is None:
        continue

      relative_pos = np.array(state["pos"], dtype=np.float32) + self.OFFSET
      gps_data = self.gps.poll()

      if gps_data:
        closest_coordinates = self._find_closest_coordinates(gps_data, relative_pos)
        self.publisher.publish(closest_coordinates)

      base_time = sleep_until_next(interval, base_time)
      
      