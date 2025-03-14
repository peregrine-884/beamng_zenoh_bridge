import zenoh

from msg import TurnIndicatorsCommand

class TurnIndicatorsSubscriber:
  def __init__(self, vehicle):
    self.vehicle = vehicle
    self.left = False
    self.right = False

  def callback(self, sample: zenoh.Sample):
    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    turn_indicators_cmd = TurnIndicatorsCommand.deserialize(payload).command

    if turn_indicators_cmd == 1:
      self.left = False
      self.right = False
    elif turn_indicators_cmd == 2:
      self.left = True
    elif turn_indicators_cmd == 3:
      self.right = True

    if not (turn_indicators_cmd == 0):
      self.vehicle.set_lights(
        left_signal = self.left,
        right_signal = self.right
      )
      