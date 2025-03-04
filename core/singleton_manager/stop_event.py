from .z_singleton_base import SingletonBase

class StopEventSingleton(SingletonBase):
  def initialize(self):
    self.stop_event = None

  def set_stop_event(self, new_value):
    self.stop_event = new_value

  def get_value(self):
    return self.stop_event.is_set()