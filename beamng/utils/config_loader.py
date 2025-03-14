import os
import json5

import os
import json5

def load_config_from_json5(config_dir, config_path):
  """
  Recursively load JSON5 configuration files, ensuring all paths are fully expanded.
  """
  def load_file(path):
    full_path = os.path.join(config_dir, path)
    print(f"Loading config from {full_path}")
    if not os.path.exists(full_path):
      raise FileNotFoundError(f"Config file not found at {full_path}")
    with open(full_path, "r") as f:
      return json5.load(f)

  # Initial data loading
  data = load_file(config_path)

  # Recursive function to expand the data
  def recursive_load(obj):
    if isinstance(obj, dict):
      for key, value in obj.items():
        # If it's a JSON5 path, load it recursively
        if isinstance(value, str) and value.endswith(".json5"):
          obj[key] = load_file(value)
          recursive_load(obj[key])  # Process the loaded data recursively
        else:
          recursive_load(value)
    elif isinstance(obj, list):
      for item in obj:
        recursive_load(item)

  recursive_load(data)
  return data

def split_data(data):
    level_and_description = {
      'level': data['map']['level'],
      'description': data['map']['description'],
    }

    ego_and_npc_vehicles = {
      'ego_vehicle': data['map']['spawn_points']['ego_vehicle'],
      'npc_vehicles': data['map']['spawn_points']['npc_vehicles']
    }

    sensors = {
      'cameras': data['sensors']['cameras'],
      'imus': data['sensors']['imus'],
      'lidars': data['sensors']['lidars'],
    }

    vehicle_interface = {
      "pub": data['vehicle']['pub'],
      "sub": data['vehicle']['sub'],
    }

    return level_and_description, ego_and_npc_vehicles, sensors, vehicle_interface
