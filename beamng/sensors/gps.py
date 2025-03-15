import time

import numpy as np

from beamngpy.sensors import GPS

from zenoh_bridge import GPSDataPublisher
from beamng.utils.sleep_until_next import sleep_until_next

class GPSManager:
  OFFSET = [0.33022292, -1.26480627, 0.77556159666]
  
  def __init__(self, bng, vehicle, vehicle_data, gps_config, zenoh_config):
    self.gps = GPS(
      gps_config['name'],
      bng,
      vehicle,
      pos=tuple(gps_config['pos']),
      ref_lon=gps_config['ref_lon'],
      ref_lat=gps_config['ref_lat'],
      is_visualised=gps_config['is_visualised'],
    )
    self.frequency = gps_config['frequency']

    self.publisher = GPSDataPublisher(zenoh_config, gps_config['topic_name'])
    
    self.vehicle_data = vehicle_data
    
    print(f'{gps_config["name"]}: {gps_config["topic_name"]}')
    
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
      state = self.vehicle_data.get_state()

      relative_pos = np.array(state["pos"], dtype=np.float32) + self.OFFSET
      gps_data = self.gps.poll()

      if gps_data:
        closest_coordinates = self._find_closest_coordinates(gps_data, relative_pos)
        self.publisher.publish(closest_coordinates)

      base_time = sleep_until_next(interval, base_time)
      
      