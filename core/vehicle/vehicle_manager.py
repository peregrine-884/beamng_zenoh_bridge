import time

import numpy as np

from beamngpy import Vehicle
from beamngpy.sensors import Electrics

from core.singleton_manager import DataPublisherSingleton, StopEventSingleton

class VehicleManager:
  def __init__(self, vehicle_data):
    self.vehicle = Vehicle(vehicle_data['name'], model=vehicle_data['model'], color=vehicle_data['color'])
    self.vehicle.sensors.attach('electrics', Electrics())
    self.state = None
    self.electrics = None
    self.data_publisher_instance = DataPublisherSingleton()
    self.stop_event_instance = StopEventSingleton()
    
    self.manual_mode = True
    
  def update_data(self, frequency):
    interval = 1.0 / frequency
    base_time = time.time()
    
    while not self.stop_event_instance.get_value():
      self.vehicle.sensors.poll()
      self.state = self.vehicle.sensors['state']
      self.electrics = self.vehicle.sensors['electrics']
    
      next_time = max(0, interval - (time.time() - base_time))
      if next_time > 0:
        time.sleep(next_time)
      base_time = time.time()
      
  def send_vehicle_info(self, frequency):
    interval = 1.0 / frequency
    base_time = time.time()
    
    while not self.stop_event_instance.get_value():
      if self.state is None or self.electrics is None:
        continue
      
      dir_vector = self.state['dir']
      vel_vector = self.state['vel']
      dir_norm = dir_vector / np.linalg.norm(dir_vector)
      longitudinal_vel = np.dot(vel_vector, dir_norm)
      
      lateral_dir = np.array([-dir_norm[1], dir_norm[0], 0])
      lateral_vel = np.dot(vel_vector, lateral_dir)
      
      steering_input = self.electrics['steering']
      steering_tire_angle = steering_input * 0.7 * -1
      
      gear_map = {'N': 1, 'R': 20, 'D': 2}
      gear_value = gear_map.get(self.electrics['gear'], 0)
      
      control_mode = 4 if self.manual_mode else 1
      
      fuel = self.electrics['fuel'] * 100
      
      hazard_report = 2 if self.electrics['hazard_signal'] else 1
      
      turn_signal = self.electrics['turnsignal']
      if turn_signal > 0.1:
        turn_report = 3
      elif turn_signal < -0.1:
        turn_report = 2
      else:
        turn_report = 1
        
      data = [
        longitudinal_vel,
        lateral_vel,
        heading_rate,
        steering_tire_angle,
        gear_value,
        control_mode,
        fuel,
        hazard_report,
        turn_report
      ]
      
      self.data_publisher_instance.vehicle_info(data)
      
      next_time = max(0, interval - (time.time() - base_time))
      if next_time > 0:
        time.sleep(next_time)
      base_time = time.time()
      
      
      
      
      
      
      
      
      