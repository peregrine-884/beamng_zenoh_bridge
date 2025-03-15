import time

import numpy as np

from zenoh_bridge import VelocityStatusPublisher as Publisher
from beamng.utils.sleep_until_next import sleep_until_next

class VelocityStatusPublisher:
  def __init__(self, vehicle_data, config_path, topic_name, frequency):
    self.vehicle_data = vehicle_data
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      state = self.vehicle_data.get_state()

      dir_vector = state['dir']
      vel_vector = state['vel']
      dir_norm = dir_vector / np.linalg.norm(dir_vector)

      longitudinal_vel = np.dot(vel_vector, dir_norm)

      lateral_dir = np.array([-dir_norm[1], dir_norm[0], 0])
      lateral_vel = np.dot(vel_vector, lateral_dir)

      self.publisher.publish(
        frame_id = 'base_link',
        longitudinal_vel = longitudinal_vel,
        lateral_vel = lateral_vel,
        heading_rate = 0.0
      )

      base_time = sleep_until_next(interval, base_time)