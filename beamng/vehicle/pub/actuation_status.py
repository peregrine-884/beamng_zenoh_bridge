import time

from zenoh_bridge import ActuationStatusPublisher as Publisher
from core.utils.sleep_until_next import sleep_until_next

class ActuationStatusPublisher:
  def __init__(self, vehicle, config_path, topic_name, frequency):
    self.vehicle = vehicle
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      electrics = self.vehicle.get_electrics()

      throttle = electrics['throttle']
      brake = electrics['brake']
      steering = electrics['steering']

      self.publisher.publish(
        frame_id = 'base_link',
        throttle = throttle,
        brake = brake,
        steering = steering
      )

      base_time = sleep_until_next(interval, base_time)