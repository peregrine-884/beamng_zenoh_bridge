import time

def send_camera_data(data_publisher, camera, stop_event):
  camera_hz = 30
  camera_interval = 1.0 / camera_hz
  base_time = time.time()
  
  while True:
    if stop_event.is_set():
      break
    
    data = camera.stream_raw()
    image_data = data['colour'].tobytes()
    
    data_publisher.process_camera(image_data)
    
    next_time = max(0, camera_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
    
    
    