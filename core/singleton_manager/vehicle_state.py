from .z_singleton_base import SingletonBase

class VehicleStateSingleton(SingletonBase):
  def initialize(self):
    self.longitudinal_vel = 0
    self.steering_tire_angle = 0
    self.heading_rate = 0
    self.manual_mode = True
    self.enable_left = False
    self.enable_right = False
    self.enable_hazard = False

  def get_longitudinal_vel(self):
    return self.longitudinal_vel

  def set_longitudinal_vel(self, new_value):
    self.longitudinal_vel = new_value

  def get_steering_tire_angle(self):
    return self.steering_tire_angle

  def set_steering_tire_angle(self, new_value):
    self.steering_tire_angle = new_value

  def get_heading_rate(self):
    return self.heading_rate

  def set_heading_rate(self, new_value):
    self.heading_rate = new_value

  def get_manual_mode(self):
    return self.manual_mode

  def set_manual_mode(self, new_value):
    self.manual_mode = new_value

  def get_enable_left(self):
    return self.enable_left

  def set_enable_left(self, new_value):
    self.enable_left = new_value

  def get_enable_right(self):
    return self.enable_right

  def set_enable_right(self, new_value):
    self.enable_right = new_value

  def get_enable_hazard(self):
    return self.enable_hazard

  def set_enable_hazard(self, new_value):
    self.enable_hazard = new_value