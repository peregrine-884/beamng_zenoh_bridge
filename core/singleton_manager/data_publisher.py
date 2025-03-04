from .z_singleton_base import SingletonBase

class DataPublisherSingleton(SingletonBase):
  def initialize(self):
    self.data_publisher = None

  def set_data_publisher(self, new_value):
    self.data_publisher = new_value

  def lidar(self, pointcloud, frame_id):
    self.data_publisher.publish_lidar_data(pointcloud, frame_id)

  def imu(self, imu_data):
    self.data_publisher.publish_imu_data(imu_data)

  def vehicle_info(self, vehicle_info):
    self.data_publisher.publish_vehicle_info(*vehicle_info)

  def vehicle_control(self, vehicle_control):
    self.data_publisher.publish_vehicle_control(*vehicle_control)

  def clock(self):
    self.data_publisher.publish_clock_data()

  def camera(self, image):
    self.data_publisher.publish_camera_data(image)

  def gps(self, gps):
    self.data_publisher.publish_gps(*gps)