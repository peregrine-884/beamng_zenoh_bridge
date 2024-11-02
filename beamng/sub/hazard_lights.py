import zenoh

from msg.autoware_vehicle_msgs import HazardLightsCommand
from shared import *

vehicle_instance = VehicleSingleton()
vehicle_state_instance = VehicleStateSingleton()

def hazard_lights_callback(sample: zenoh.Sample):
    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    hazard_lights_cmd = HazardLightsCommand.deserialize(payload).command
    
    if hazard_lights_cmd == 1:
        vehicle_state_instance.set_enable_hazard(False)
    elif hazard_lights_cmd == 2:
        vehicle_state_instance.set_enable_hazard(True)
        
    if not (hazard_lights_cmd == 0):        
        vehicle_instance.set_lights(
            left_signal = vehicle_state_instance.get_enable_left(),
            right_signal = vehicle_state_instance.get_enable_right(),
            hazard_signal=vehicle_state_instance.get_enable_hazard()
        )