import time

from zenoh_bridge import ClockDataPublisher
from beamng.utils.sleep_until_next import sleep_until_next

class ClockManager:
  def __init__(self, clock_config, zenoh_config):
    self.frequency = clock_config['frequency']

    self.publisher = ClockDataPublisher(zenoh_config, clock_config['topic_name'])
    
    print(f'Clock: {clock_config["topic_name"]}')
    
  def send(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event.is_set():
      self.publisher.publish()
      
      base_time = sleep_until_next(interval, base_time)