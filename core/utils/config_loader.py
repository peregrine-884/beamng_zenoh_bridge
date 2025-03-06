import json5

def load_config_from_json5(json5_path):
  with open(json5_path, 'r') as f:
    return json5.load(f)
  

def print_formatted_data(data):
  for key, value in data.items():
    print(f"=== {key.upper()} ===")
    
    if isinstance(value, list):
      if len(value) == 0:
        print("  (empty)")
      for item in value:
        if isinstance(item, dict) and "name" in item:
          print(f"- {item['name']}")
        for sub_key, sub_value in item.items():
          print(f"  {sub_key}: {sub_value}")
        print("-" * 50)
    
    elif isinstance(value, dict):
      for sub_key, sub_value in value.items():
        print(f"  {sub_key}: {sub_value}")
    
    else:
      print(f"  {value}")

    print("\n")