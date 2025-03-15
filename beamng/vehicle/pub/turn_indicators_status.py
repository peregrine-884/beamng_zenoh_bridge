import time

from zenoh_bridge import TurnIndicatorsStatusPublisher as Publisher
from beamng.utils.sleep_until_next import sleep_until_next

class TurnIndicatorsStatusPublisher:
  def __init__(self, vehicle_data, config_path, topic_name, frequency):
    self.vehicle_data = vehicle_data
    self.publisher = Publisher(config_path, topic_name)
    self.frequency = frequency

  def publish(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()

    while not stop_event.is_set():
      electrics = self.vehicle_data.get_electrics()

      # 1: Disable, 2: Enable_Left, 3: Enable_Right
      turn_signal = electrics['turnsignal']
      if turn_signal > 0.1:
        turn_signal_state = 3
      elif turn_signal < -0.1:
        turn_signal_state = 2
      else:
        turn_signal_state = 1
      
      self.publisher.publish(
        turn_signal = turn_signal_state
      )

      base_time = sleep_until_next(interval, base_time)