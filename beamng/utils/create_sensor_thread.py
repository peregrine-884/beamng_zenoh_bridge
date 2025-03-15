import threading

def create_sensor_thread(sensor_manager, stop_event):
  thread = threading.Thread(target=sensor_manager.send, args=(stop_event,))
  thread.start()
  return thread