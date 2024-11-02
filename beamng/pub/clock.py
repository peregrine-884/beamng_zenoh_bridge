import time

from shared import *

def send_clock_data():
	data_publisher_instance = DataPublisherSingleton()
	stop_event_instance = StopEventSingleton()
  
	clock_hz = 100
	clock_interval = 1.0 / clock_hz
	base_time = time.time()

	while True:
			if stop_event_instance.get_value():
					break
			
			data_publisher_instance.clock()
			
			next_time = max(0, clock_interval - (time.time() - base_time))
			time.sleep(next_time)
			base_time = time.time()