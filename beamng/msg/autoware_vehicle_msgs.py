from pycdr2 import IdlStruct
from pycdr2.types import uint8
from dataclasses import dataclass

from .builtin_interfaces import Time

@dataclass
class TurnIndicatorsCommand(IdlStruct, typename="TurnIndicatorsCommand"):
    stamp: Time
    command: uint8
    
@dataclass
class HazardLightsCommand(IdlStruct, typename="HazardLightsCommand"):
    stamp: Time
    command: uint8