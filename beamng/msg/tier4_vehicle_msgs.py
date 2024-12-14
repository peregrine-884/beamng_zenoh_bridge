from pycdr2 import IdlStruct
from pycdr2.types import float64
from dataclasses import dataclass

from msg.std_msgs import Header

@dataclass
class ActuationCommand(IdlStruct, typename="ActuationCommand"):
  accel_cmd: float64
  brake_cmd: float64
  steer_cmd: float64
  
@dataclass
class ActuationCommandStamped(IdlStruct, typename="ActuationCommandStamped"):
  header: Header
  actuation: ActuationCommand
