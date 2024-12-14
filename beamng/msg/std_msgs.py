from pycdr2 import IdlStruct
from dataclasses import dataclass

from msg.builtin_interfaces import Time

@dataclass
class Header(IdlStruct, typename="Header"):
    stamp: Time
    frame_id: str