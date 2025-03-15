import time

from zenoh_bridge import HazardLightsStatusPublisher as Publisher
from beamng.utils.sleep_until_next import sleep_until_next

class HazardLightsStatusPublisher:
  def __init__(self, vehicle_data, config_path, topic_name, frequency):
    self.vehicle_data = vehicle_data
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      electrics = self.vehicle_data.get_electrics()

      # 1: Enable, 2: Disable
      hazard_signal = 2 if electrics['hazard_signal'] else 1

      self.publisher.publish(
        hazard = hazard_signal,
      )

      base_time = sleep_until_next(interval, base_time)