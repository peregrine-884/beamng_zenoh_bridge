import time

from beamngpy.sensors import Electrics

from beamng.utils.sleep_until_next import sleep_until_next

class VehicleData:
  def __init__(self, vehicle):
    self.vehicle = vehicle
    self.vehicle.sensors.attach('electrics', Electrics())
    self.state = None
    self.electrics = None
    self.manual_mode = True
    
  def update_data(self, stop, frequency):
    interval = 1.0 / frequency
    base_time = time.time()

    while not stop.is_set():
      self.vehicle.sensors.poll()
      self.state = self.vehicle.sensors['state']
      self.electrics = self.vehicle.sensors['electrics']

      base_time = sleep_until_next(interval, base_time)
      
  def get_state(self):
    return self.state
  
  def get_electrics(self):
    return self.electrics
  
  def get_manual_mode(self):
    return self.manual_mode
  
  def set_manual_mode(self, manual_mode):
    self.manual_mode = manual_mode