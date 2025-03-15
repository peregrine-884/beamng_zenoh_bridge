import zenoh

from beamng.msg.autoware_vehicle_msgs import HazardLightsCommand

class HazardLightsSubscriber:
  def __init__(self, vehicle):
    self.vehicle = vehicle
    self.hazard_lights = False

  def callback(self, sample: zenoh.Sample):
    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    hazard_lights_cmd = HazardLightsCommand.deserialize(payload).command

    if hazard_lights_cmd == 1:
      self.hazard_lights = False
    elif hazard_lights_cmd == 2:
      self.hazard_lights = True

    if not (hazard_lights_cmd == 0):
      self.vehicle.set_lights(
        hazard_signal = self.hazard_lights
      )