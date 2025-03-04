import numpy as np
import time

from singleton_manager import DataPublisherSingleton, StopEventSingleton, VehicleStateSingleton, VehicleSingleton

def send_vehicle_info_data():
	data_publisher_instance = DataPublisherSingleton()
	vehicle_instance = VehicleSingleton()
	stop_event_instance = StopEventSingleton()
	vehicle_state_instance = VehicleStateSingleton()
	
	vehicle_hz = 10
	vehicle_interval = 1.0 / vehicle_hz
	base_time = time.time()
	
	while True:
		if stop_event_instance.get_value():
			break
		
		state = vehicle_instance.get_state()
		electrics = vehicle_instance.get_electrics()
  
		if state is None or electrics is None:
			continue
		
		# velocity m/s
		dir = state['dir']
		vel = state['vel']
		
		dir_norm = dir / np.linalg.norm(dir)
		longitudinal_vel = np.dot(vel, dir_norm)
		vehicle_state_instance.set_longitudinal_vel(longitudinal_vel)
		
		lateral_dir = np.array([-dir_norm[1], dir_norm[0], 0])
		lateral_vel = np.dot(vel, lateral_dir)
		
		# steering 
		# Set the vehicle's maximum steering angle to 0.7 [rad]
		# The value obtained from BeamNG is left (negative) and right (positive),
		# while Autoware requires left (positive) and right (negative).
		# Therefore, the value is converted accordingly.
		steering_input = electrics['steering_input']
		steering_tire_angle = steering_input * 0.7 * -1
		vehicle_state_instance.set_steering_tire_angle(steering_tire_angle)
		
		# gear
		gear = electrics['gear']
		if gear == 'N':
				gear_value = 1
		elif gear == 'R':
				gear_value = 20
		elif gear == 'D':
				gear_value = 2
		else:
				gear_value = 0
				
		# control_mode
		control_mode = 4 if vehicle_state_instance.get_manual_mode() else 1
		
		# battery
		fuel = electrics['fuel'] * 100
		
		# hazard_light
		hazard_signal = electrics['hazard_signal']
		hazard_report = 2 if hazard_signal else 1
		
		# turn_indicators
		turn_signal = electrics['turnsignal']
		if turn_signal > 0.1:
				turn_report = 3
		elif turn_signal < -0.1:
				turn_report = 2
		else:
				turn_report = 1
				
		vehicle_status = [
				longitudinal_vel,
				lateral_vel,
				vehicle_state_instance.get_heading_rate(),
				steering_tire_angle,
				gear_value,
				control_mode,
				fuel,
				hazard_report,
				turn_report
		]
	
		data_publisher_instance.vehicle_info(vehicle_status)
		
		next_time = max(0, vehicle_interval - (time.time() - base_time))
		time.sleep(next_time)
		base_time = time.time()