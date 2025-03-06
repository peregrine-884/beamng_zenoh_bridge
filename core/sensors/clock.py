import time

from core.singleton_manager import DataPublisherSingleton, StopEventSingleton

class ClockManager:
  def __init__(self, frequency):
    self.frequency = frequency
    
  def send(self):
    data_publisher_instance = DataPublisherSingleton()
    stop_event_instance = StopEventSingleton()
    
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event_instance.get_value():
      data_publisher_instance.clock()
      
      next_time = max(0, interval - (time.time() - base_time))
      if next_time > 0:
        time.sleep(next_time)
      base_time = time.time()