from shared import *
import time

def accel_map():
  vehicle_instance = VehicleSingleton()
  vehicle_state_instance = VehicleStateSingleton()
  stop_event_instance = StopEventSingleton()
  
  num_loops = 150
  exit_loop = False  # ループを抜けるためのフラグ
  flag = False
  
  accels = [round(i * 0.05, 2) for i in range(1, 21)]
  accels.reverse()

  for accel in accels:
      print(f"================== Accelerating with {accel} ==================")
  
      time.sleep(3)
      
      for i in range(num_loops):
          print(f"================== Loop {i} ==================")

          time.sleep(3)
          
          set_control_executed = False  # `set_control` が実行されたかを示すフラグ
          while True:
              if stop_event_instance.get_value():  # stop_event_instanceがTrueならループ終了
                  exit_loop = True
                  break
              
              if vehicle_state_instance.get_manual_mode():
                  vehicle_instance.set_control(
                      steering=0.0,
                      throttle=0.0,
                      brake=0.0
                  )
                  
                  vehicle_instance.vehicle.teleport(
                      pos=(-1020.482, 0.000, 0.600), 
                      rot_quat=(0.0, 0.0, -0.70710678, 0.70710678), 
                      reset=True
                  )
                  
                  vehicle_state_instance.set_manual_mode(False)
                  
                  flag = False
                  break

              state = vehicle_instance.get_state()
              if state is None:
                  continue

              position = state["pos"]
              velocity = vehicle_state_instance.get_longitudinal_vel()

              if not set_control_executed:
                  # 一度だけ `set_control` を実行
                  vehicle_instance.set_control(
                      steering=0.0,
                      throttle=accel,
                      brake=0.0
                  )
                  set_control_executed = True  # 実行済みにする
                  print("Control command executed.")

              if (position[0] > 500) or (velocity > 30.0):
                  vehicle_instance.set_control(
                      steering=0.0,
                      throttle=0.0,
                      brake=0.0
                  )
                  
                  vehicle_instance.vehicle.teleport(
                      pos=(-1020.482, 0.000, 0.600), 
                      rot_quat=(0.0, 0.0, -0.70710678, 0.70710678), 
                      reset=True
                  )
                  break

          if exit_loop:  # 内側のforループも終了
              break
          
          if flag:
              flag = False
              break

      if exit_loop:  # 最外のforループも終了
          break

  print("All loops exited.")

