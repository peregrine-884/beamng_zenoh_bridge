from .z_singleton_base import SingletonBase

class VehicleSingleton(SingletonBase):
  def initialize(self):
    self.vehicle = None
    self.sensor_initialized = False

  def set_vehicle(self, new_value):
    self.vehicle = new_value
    self.sensor_initialized = False

  def set_control(self, steering, throttle, brake):
    self.vehicle.control(steering, throttle, brake)

  def set_lights(self, left_signal, right_signal, hazard_signal):
    self.vehicle.set_lights(left_signal, right_signal, hazard_signal)

  def get_sensor_data(self):
    self.vehicle.sensors.poll()
    self.sensor_initialized = True

  def get_state(self):
    if not self.sensor_initialized:
      return None
    return self.vehicle.sensors['state']

  def get_electrics(self):
    if not self.sensor_initialized:
      return None
    return self.vehicle.sensors['electrics']