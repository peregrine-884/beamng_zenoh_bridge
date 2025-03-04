from singleton_manager import VehicleStateSingleton, VehicleSingleton
import time

def brake_map():
  vehicle_instance = VehicleSingleton()
  vehicle_state_instance = VehicleStateSingleton()

  num_loops = 150
  flag = False

  brakes = [round(i * 0.05, 2) for i in range(21)][::-1]

  for brake in brakes:
    print(f"================== Braking with {brake} ==================")
    time.sleep(3)

    for i in range(num_loops):
      print(f"================== Loop {i} ==================")
      time.sleep(2)

      vehicle_instance.vehicle.control(gear=2, parkingbrake=0.0)
      set_control_executed = False
      set_brake_executed = False

      while True:
        if vehicle_state_instance.get_manual_mode():
          vehicle_state_instance.set_manual_mode(False)
          vehicle_instance.set_control(steering=0.0, throttle=0.0, brake=0.0)
          vehicle_instance.vehicle.teleport(
            pos=(-1020.482, 0.000, 0.600),
            rot_quat=(0.0, 0.0, -0.70710678, 0.70710678),
            reset=True
          )
          flag = True
          break

        state = vehicle_instance.get_state()
        if state is None:
          continue

        position = state["pos"]
        velocity = vehicle_state_instance.get_longitudinal_vel()

        if not set_control_executed:
          vehicle_instance.set_control(steering=0.0, throttle=1.0, brake=0.0)
          set_control_executed = True
          print("Control command executed.")

        if velocity > 40.0 and not set_brake_executed:
          vehicle_instance.set_control(steering=0.0, throttle=0.0, brake=brake)
          set_brake_executed = True

        if set_brake_executed and (velocity < -0.1 or position[0] > -100):
          vehicle_instance.set_control(steering=0.0, throttle=0.0, brake=0.0)
          vehicle_instance.vehicle.teleport(
            pos=(-1020.482, 0.000, 0.600),
            rot_quat=(0.0, 0.0, -0.70710678, 0.70710678),
            reset=True
          )
          break

      if flag:
        flag = False
        break

  print("All loops exited.")
