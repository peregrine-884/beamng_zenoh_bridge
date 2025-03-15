from beamng.vehicle.publishers import VehiclePublishers
from beamng.vehicle.subscribers import VehicleSubscribers

class VehicleInterface:
  def __init__(self, vehicle, vehicle_data, interface_config, config_path):
    self.publishers = VehiclePublishers(
      vehicle_data,
      config_path,
      interface_config['pub']
    )
    
    self.subscribers = VehicleSubscribers(
      vehicle,
      vehicle_data,
      config_path,
      interface_config['sub']
    )
    
  def start_communication(self, stop_event):
    self.publishers.start(stop_event)
    
  def stop_communication(self):
    self.publishers.join()
    self.subscribers.close()
