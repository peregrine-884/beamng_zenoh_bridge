import time

from zenoh_bridge import ClockDataPublisher
from core.utils.sleep_until_next import sleep_until_next

class ClockManager:
  def __init__(self, frequency, config_path, topic_name):
    self.frequency = frequency

    self.publisher = ClockDataPublisher(config_path, topic_name)
    
  def send(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event.is_set():
      self.publisher.publish()
      
      base_time = sleep_until_next(interval, base_time)