import time

from singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleSingleton

def send_vehicle_control_data():
  data_publisher_instance = DataPublisherSingleton()
  vehicle_instance = VehicleSingleton()
  stop_event_instance = StopEventSingleton()
  
  vehicle_control_hz = 10
  vehicle_control_interval = 1.0 / vehicle_control_hz
  base_time = time.time()
  
  while True:
    if stop_event_instance.get_value():
      break
    
    electrics = vehicle_instance.get_electrics()
    
    if electrics is None:
      continue
  
    # vehicle control
    throttle = electrics['throttle_input']
    brake = electrics['brake_input']
    steering = electrics['steering_input']

    vehicle_control = [
        throttle,
        brake,
        steering
    ]
    
    # print(vehicle_control)
    
    data_publisher_instance.vehicle_control(vehicle_control)
    
    next_time = max(0, vehicle_control_interval - (time.time() - base_time))
    time.sleep(next_time)
    base_time = time.time()
