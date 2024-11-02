from pycdr2 import IdlStruct
from pycdr2.types import uint32, int32
from dataclasses import dataclass

@dataclass
class Time(IdlStruct, typename="Time"):
    sec: int32
    nanosec: uint32