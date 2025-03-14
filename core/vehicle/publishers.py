import threading

from zenoh_bridge import (
  ActuationStatusPublisher,
  BatteryChargePublisher,
  ControlModePublisher,
  GearStatusPublisher,
  HazardLightsStatusPublisher,
  SteeringStatusPublisher,
  TurnIndicatorsStatusPublisher,
  VelocityStatusPublisher
)

class VehiclePublishers:
  def __init__(self, vehicle, config_path, publisher_configs):
    self.publishers = {}
    self.threads = []

    for key, config in publisher_configs.items():
      publisher_class = globals().get(f'{key.capitalize()}Publisher')
      if publisher_class:
        self.publishers[key] = publisher_class(
          vehicle,
          config_path,
          config['topic_name'],
          config['frequency']
        )

  def start(self, stop_event):
    for publisher in self.publishers.values():
      thread = threading.Thread(target=publisher.publish, args=(stop_event,))
      thread.start()
      self.threads.append(thread)

  def join(self):
    for thread in self.threads:
      thread.join()
