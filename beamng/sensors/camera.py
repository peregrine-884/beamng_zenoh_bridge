import time

from beamngpy.sensors import Camera

from zenoh_bridge import CameraDataPublisher
from beamng.utils.sleep_until_next import sleep_until_next

class CameraManager:
  def __init__(self, bng, vehicle, camera_config, zenoh_config):
    self.camera = Camera(
      camera_config['name'],
      bng,
      vehicle,
      requested_update_time=camera_config['requested_update_time'],
      pos=tuple(camera_config['pos']),
      dir=tuple(camera_config['dir']),
      up=tuple(camera_config['up']),
      resolution=tuple(camera_config['resolution']),
      near_far_planes=tuple(camera_config['near_far_planes']),
      is_using_shared_memory=camera_config['is_using_shared_memory'],
      is_render_annotations=camera_config['is_render_annotations'],
      is_render_instance=camera_config['is_render_instance'],
      is_render_depth=camera_config['is_render_depth'],
      is_visualised=camera_config['is_visualised'],
      is_streaming=camera_config['is_streaming'],
      is_dir_world_space=camera_config['is_dir_world_space'],
    )
    self.frequency = camera_config['frequency']
    self.frame_id = camera_config['frame_id']
    
    self.publisher = CameraDataPublisher(zenoh_config, camera_config['topic_name'])
    
    self.width = camera_config['resolution'][0]
    self.height = camera_config['resolution'][1]
    
    print(f'{camera_config["name"]}: {camera_config["topic_name"]}')
    
  def send(self, stop_event):
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event.is_set():
      data = self.camera.stream_raw()
      image_data = data['colour'].tobytes()
      
      self.publisher.publish(self.frame_id, image_data, self.width, self.height)
      
      base_time = sleep_until_next(interval, base_time)