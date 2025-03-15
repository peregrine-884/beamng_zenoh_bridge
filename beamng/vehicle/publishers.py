import threading

from beamng.vehicle.pub import (
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
  def __init__(self, vehicle_data, config_path, publisher_configs):
    self.publishers = {}
    self.threads = []

    for key, config in publisher_configs.items():
      string = ''.join(word.capitalize() for word in key.split('_'))
      publisher_class = globals().get(f'{string}Publisher')
      if publisher_class:
        self.publishers[key] = publisher_class(
          vehicle_data,
          config_path,
          config['topic_name'],
          config['frequency']
        )
        
        print(f'Publisher {config["topic_name"]}')

  def start(self, stop_event):
    for publisher in self.publishers.values():
      thread = threading.Thread(target=publisher.publish, args=(stop_event,))
      thread.start()
      self.threads.append(thread)

  def join(self):
    for thread in self.threads:
      thread.join()
