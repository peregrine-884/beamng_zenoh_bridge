import zenoh

from zenoh_bridge import (
  ActuationControlSubscriber,
  HazardLightsSubscriber,
  TurnIndicatorsSubscriber
)

class VehicleSubscribers:
  def __init__(self, vehicle, config_path, subscriber_config):
    config = zenoh.Config.from_file(config_path)
    self.session = zenoh.open(config)

    self.subscriptions = {}
    for key, topic in subscriber_config.items():
      subscriber_class = globals().get(f'{key.capitalize()}Subscriber')
      if subscriber_class:
        subscriber = subscriber_class(vehicle)
        self.subscriptions[key] = self.session.declare_subscriber(topic, subscriber.callback)

  def close(self):
    for subscription in self.subscriptions.values():
      subscription.undeclare()

    self.session.close()
