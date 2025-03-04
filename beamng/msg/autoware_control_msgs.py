from pycdr2 import IdlStruct
from pycdr2.types import float32
from dataclasses import dataclass

from .builtin_interfaces import Time
    
@dataclass
class Lateral(IdlStruct, typename="Lateral"):
    stamp: Time
    control_time: Time
    steering_tire_angle: float32
    steering_tire_rotation_rate: float32
    is_defined_steering_tire_rotation_rate: bool

@dataclass
class Longitudinal(IdlStruct, typename="Longitudinal"):
    stamp: Time
    control_time: Time
    velocity: float32
    acceleration: float32
    jerk: float32
    is_defined_acceleration: bool
    is_defined_jerk: bool
    
@dataclass
class Control(IdlStruct, typename="Control"):
    stamp: Time
    control_time: Time
    lateral: Lateral
    longitudinal: Longitudinal