import time

from zenoh_bridge import ControlModePublisher as Publisher
from core.utils.sleep_until_next import sleep_until_next

class ControlModePublisher:
  def __init__(self, vehicle, config_path, topic_name, frequency):
    self.vehicle = vehicle
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      # 1: Autonomous, 4: Manual
      control_mode = 4 if self.vehicle.get_manual_mode() else 1

      self.publisher.publish(
        control_mode = control_mode
      )

      base_time = sleep_until_next(interval, base_time)