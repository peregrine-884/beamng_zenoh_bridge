import time

from beamngpy import Vehicle
from beamngpy.sensors import Electrics

from core.vehicle.publishers import VehiclePublishers
from core.vehicle.subscribers import VehicleSubscribers

class VehicleInterface:
  def __init__(self, vehicle_data, vehicle_config, config_path):
    self.vehicle = Vehicle(vehicle_data['name'], model=vehicle_data['model'], color=vehicle_data['color'])
    self.vehicle.sensors.attach('electrics', Electrics())
    self.state = None
    self.electrics = None
    self.manual_mode = True

    self.publishers = VehiclePublishers(
      self.vehicle,
      config_path,
      vehicle_config['pub']
    )
    
    self.subscribers = VehicleSubscribers(
      self.vehicle,
      config_path,
      vehicle_config['sub']
    )
    
  def start_communication(self, stop_event):
    while self.state is None or self.electrics is None:
      time.sleep(0.1)
      
    self.publishers.start(stop_event)
    
  def stop_communication(self):
    self.publishers.join()
    self.subscribers.close()

  def update_data(self, stop_event, frequency):
    interval = 1.0 / frequency
    base_time = time.time()

    while not stop_event.is_set():
      self.vehicle.sensors.poll()
      self.state = self.vehicle.sensors['state']
      self.electrics = self.vehicle.sensors['electrics']
      self.publish_data()

      next_time = max(0, interval - (time.time() - base_time))
      if next_time > 0:
        time.sleep(next_time)
      base_time = time.time()
      
  def get_state(self):
    return self.state
  
  def get_electrics(self):
    return self.electrics
  
  def get_manual_mode(self):
    return self.manual_mode
  
  def set_manual_mode(self, manual_mode):
    self.manual_mode = manual_mode