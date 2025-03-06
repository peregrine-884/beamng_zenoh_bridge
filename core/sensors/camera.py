import time

from beamngpy.sensors import Camera

from core.singleton_manager import DataPublisherSingleton, StopEventSingleton

class CameraManager:
  def __init__(self, bng, vehicle, camera_data):
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
    
  def send(self):
    data_publisher_instance = DataPublisherSingleton()
    stop_event_instance = StopEventSingleton()
    
    interval = 1.0 / self.frequency
    base_time = time.time()
    
    while not stop_event_instance.get_value():
      data = self.camera.stream_raw()
      image_data = data['colour'].tobytes()
      
      data_publisher_instance.camera(image_data)
      
      next_time = max(0, interval - (time.time() - base_time))
      if next_time > 0:
        time.sleep(next_time)
      base_time = time.time()