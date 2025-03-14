import time

from zenoh_bridge import SteeringStatusPublisher as Publisher
from core.utils.sleep_until_next import sleep_until_next

class SteeringStatusPublisher:
  def __init__(self, vehicle, config_path, topic_name, frequency):
    self.vehicle = vehicle
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      electrics = self.vehicle.get_electrics()

      # Convert steering wheel input to tire angle.
      # The steering wheel input (-1 to 1) is mapped to the tire angle.
      # The maximum tire angle is set to 0.7 rad.
      # BeamNG: Left (negative), Right (positive)
      # Autoware: Left (positive), Right (negative)
      # Invert sign to match Autoware's convention.
      steering = electrics['steering']
      steering_tire_angle = steering * 0.7 * -1

      self.publisher.publish(
        steering_tire_angle = steering_tire_angle
      )

      base_time = sleep_until_next(interval, base_time)