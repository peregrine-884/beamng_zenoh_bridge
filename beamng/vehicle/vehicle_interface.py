from beamng.vehicle.publishers import VehiclePublishers
from beamng.vehicle.subscribers import VehicleSubscribers

class VehicleInterface:
  def __init__(self, vehicle, vehicle_data, interface_config, zenoh_config):
    self.publishers = VehiclePublishers(
      vehicle_data,
      zenoh_config,
      interface_config['pub']
    )
    
    self.subscribers = VehicleSubscribers(
      vehicle,
      vehicle_data,
      zenoh_config,
      interface_config['sub']
    )
    
  def start_communication(self, stop_event):
    self.publishers.start(stop_event)
    
  def stop_communication(self):
    self.publishers.join()
    self.subscribers.close()
