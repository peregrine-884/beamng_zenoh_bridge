import time

from beamngpy.sensors import Camera

from zenoh_bridge import CameraDataPublisher
from core.utils.sleep_until_next import sleep_until_next

class CameraManager:
  def __init__(self, bng, vehicle, camera_data, config_path):
    self.camera = Camera(
      camera_data['name'],
      bng,
      vehicle,
      requested_update_time=camera_data['requested_update_time'],
      pos=tuple(camera_data['pos']),
      dir=tuple(camera_data['dir']),
      up=tuple(camera_data['up']),
      resolution=tuple(camera_data['resolution']),
      near_far_planes=tuple(camera_data['near_far_planes']),
      is_using_shared_memory=camera_data['is_using_shared_memory'],
      is_render_annotations=camera_data['is_render_annotations'],
      is_render_instance=camera_data['is_render_instance'],
      is_render_depth=camera_data['is_render_depth'],
      is_visualised=camera_data['is_visualised'],
      is_streaming=camera_data['is_streaming'],
      is_dir_world_space=camera_data['is_dir_world_space'],
    )
    self.frequency = camera_data['frequency']
    
    self.publisher = CameraDataPublisher(config_path, camera_data['topic_name'])
    
  def send(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event.is_set():
      data = self.camera.stream_raw()
      image_data = data['colour'].tobytes()
      
      self.publisher.publish(image_data)
      
      base_time = sleep_until_next(interval, base_time)