import zenoh

from msg.autoware_vehicle_msgs import TurnIndicatorsCommand
from singleton_manager import VehicleStateSingleton, VehicleSingleton

vehicle_instance = VehicleSingleton()
vehicle_state_instance = VehicleStateSingleton()

def turn_indicators_callback(sample: zenoh.Sample):
    print("--------------------------------------- turn_indicators_callback")
    
    payload_bytes = bytes(sample.payload)
    payload = bytearray(payload_bytes)
    turn_indicators_cmd = TurnIndicatorsCommand.deserialize(payload).command
    
    if turn_indicators_cmd == 1:
        vehicle_state_instance.set_enable_left(False)
        vehicle_state_instance.set_enable_right(False)
    elif turn_indicators_cmd == 2:
        vehicle_state_instance.set_enable_left(True)
    elif turn_indicators_cmd == 3:
        vehicle_state_instance.set_enable_right(True)
        
    if not (turn_indicators_cmd == 0):
        vehicle_instance.set_lights(
            left_signal = vehicle_state_instance.get_enable_left(),
            right_signal = vehicle_state_instance.get_enable_right(),
            hazard_signal=vehicle_state_instance.get_enable_hazard()
        )