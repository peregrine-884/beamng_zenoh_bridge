import time

from zenoh_bridge import GearStatusPublisher as Publisher
from core.utils.sleep_until_next import sleep_until_next

class GearStatusPublisher:
  def __init__(self, vehicle, config_path, topic_name, frequency):
    self.vehicle = vehicle
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

    self.gear_map = {'N': 1, 'R': 20, 'D': 2}

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      electrics = self.vehicle.get_electrics()

      gear = self.gear_map.get(electrics['gear'], 0)

      self.publisher.publish(
        gear = gear
      )

      base_time = sleep_until_next(interval, base_time)