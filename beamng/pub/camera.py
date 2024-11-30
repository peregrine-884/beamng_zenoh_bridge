import time

from shared import *

def send_camera_data(camera):
  data_publisher = DataPublisherSingleton()
  stop_event_instance = StopEventSingleton()
  
  camera_hz = 50
  camera_interval = 1.0 / camera_hz
  base_time = time.time()
  
  while True:
    if stop_event_instance.get_value():
      break
    
    data = camera.stream_raw()
    image_data = data['colour'].tobytes()
    
    data_publisher.camera(image_data)
    
    next_time = max(0, camera_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
    
    
    