import zenoh

from beamng.vehicle.sub import (
  ActuationControlSubscriber,
  HazardLightsSubscriber,
  TurnIndicatorsSubscriber
)

class VehicleSubscribers:
  def __init__(self, vehicle, vehicle_data, config_path, subscriber_config):
    config = zenoh.Config.from_file(config_path)
    self.session = zenoh.open(config)

    self.subscriptions = {}
    for key, topic in subscriber_config.items():
      string = ''.join(word.capitalize() for word in key.split('_'))
      subscriber_class = globals().get(f'{string}Subscriber')
      if subscriber_class:
        if issubclass(subscriber_class, ActuationControlSubscriber):
          subscriber = subscriber_class(vehicle, vehicle_data)
        else:
          subscriber = subscriber_class(vehicle)
        self.subscriptions[key] = self.session.declare_subscriber(topic, subscriber.callback)
        
        print(f'Subscriber {topic}')

  def close(self):
    for subscription in self.subscriptions.values():
      subscription.undeclare()

    self.session.close()
