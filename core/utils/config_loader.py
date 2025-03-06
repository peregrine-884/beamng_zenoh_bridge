import os
import json5

def load_config_from_json5(config_dir, config_path):
  config_path = os.path.join(config_dir, config_path)
  print(f"Loading config from {config_path}")
  
  if not os.path.exists(config_path):
    raise FileNotFoundError(f"Config file not found at {config_path}")
  
  with open(config_path, "r") as f:
    data = json5.load(f)

  if "map" in data:
    map_path = os.path.join(config_dir, data["map"])
    map_data = load_config_from_json5(config_dir, data["map"])
    data["map_data"] = map_data

  if "sensors" in data:
    for sensor_type, sensor_file in data["sensors"].items():
      sensor_file_path = os.path.join(config_dir, sensor_file)
      print(f"{sensor_type.capitalize()} sensor file path: {sensor_file_path}")
      sensor_data = load_config_from_json5(config_dir, sensor_file)
      data[sensor_type] = sensor_data
  
  if "spawn_points" in data:
    spawn_file = data["spawn_points"]
    spawn_file_path = os.path.join(config_dir, spawn_file)
    print(f"Spawn point file path: {spawn_file_path}")
    spawn_data = load_config_from_json5(config_dir, spawn_file_path)
    data["spawn_points_data"] = spawn_data

  return data

def split_data_from_config(data):
    level_and_description = {
        'level': data['map_data']['level'],
        'description': data['map_data']['description']
    }

    ego_and_npc_vehicles = {
        'ego_vehicle': data['map_data']['spawn_points_data']['ego_vehicle'],
        'npc_vehicles': data['map_data']['spawn_points_data']['npc_vehicles']
    }

    sensors = {
        'cameras': data['cameras'],
        'imus': data['imus'],
        'lidars': data['lidars']
    }

    return level_and_description, ego_and_npc_vehicles, sensors
