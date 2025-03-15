import time

import numpy as np

def accel_map(vehicle, vehicle_data):
  num_loops = 150
  flag = False
  
  accels = [round(i * 0.05, 2) for i in range(1, 21)][::-1]
  
  vehicle_data.set_manual_mode(False)

  for accel in accels:
    print(f"================== Accelerating with {accel} ==================")
    time.sleep(3)
    
    for i in range(num_loops):
      print(f"================== Loop {i} ==================")
      time.sleep(2)

      vehicle.control(gear=2, parkingbrake=0.0)
      set_control_executed = False

      while True:  
        if vehicle_data.get_manual_mode():
          vehicle.control(steering=0.0, throttle=0.0, brake=0.0)
          vehicle.teleport(
            pos=(-1020.482, 0.000, 0.600),
            rot_quat=(0.0, 0.0, -0.70710678, 0.70710678),
            reset=True
          )
          vehicle_data.set_manual_mode(False)
          flag = True
          break

        state = vehicle_data.get_state()
        if state is None:
          continue

        position = state["pos"]
        
        dir_vector = state['dir']
        vel_vector = state['vel']
        dir_norm = dir_vector / np.linalg.norm(dir_vector)
        velocity = np.dot(vel_vector, dir_norm)

        if not set_control_executed:
          vehicle.control(steering=0.0, throttle=accel, brake=0.0)
          set_control_executed = True
          print("Control command executed.")

        if position[0] > 500 or velocity > 30.0:
          vehicle.control(steering=0.0, throttle=0.0, brake=0.0)
          vehicle.teleport(
            pos=(-1020.482, 0.000, 0.600),
            rot_quat=(0.0, 0.0, -0.70710678, 0.70710678),
            reset=True
          )
          break

      if flag:
        flag = False
        break

  print("All loops exited.")
