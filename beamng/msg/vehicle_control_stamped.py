from pycdr2 import IdlStruct
from pycdr2.types import float32
from dataclasses import dataclass

from msg.builtin_interfaces import Time

@dataclass
class VehicleControlStamped(IdlStruct, typename="VehicleControlStamped"):
  stamp: Time
  throttle: float32
  brake: float32
  steering: float32
