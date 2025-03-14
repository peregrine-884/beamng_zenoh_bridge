import time

from zenoh_bridge import BatteryChargePublisher as Publisher
from core.utils.sleep_until_next import sleep_until_next

class BatteryChargePublisher:
  def __init__(self, vehicle, config_path, topic_name, frequency):
    self.vehicle = vehicle
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      electrics = self.vehicle.get_electrics()

      fuel = electrics['fuel'] * 100

      self.publisher.publish(
        battery = fuel
      )

      base_time = sleep_until_next(interval, base_time)