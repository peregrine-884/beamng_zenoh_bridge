class DataPublisherSingleton:
  _instance = None
  
  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance.data_publisher = None
    
    return cls._instance
  
  def set_data_publisher(self, new_value):
    self.data_publisher = new_value
    
  def lidar(self, pointcloud):
    self.data_publisher.process_pointcloud(pointcloud)
    
  def imu(self, imu_data):
    self.data_publisher.process_imu(imu_data)
    
  def vehicle_info(self, vehicle_info):
    self.data_publisher.process_vehicle_status(*vehicle_info)
    
  def clock(self):
    self.data_publisher.publish_clock()
    
  def camera(self, image):
    self.data_publisher.process_camera(image)
    
    
class VehicleSingleton:
  _instance = None
  
  def __new__(cls):
    if cls._instance is None:
        cls._instance = super().__new__(cls)
        cls._instance.vehicle = None
    return cls._instance
  
  def set_vehicle(self, new_value):
    self.vehicle = new_value
    
  def set_control(self, steering, throttle, brake):
    self.vehicle.control(
      steering,
      throttle,
      brake
    )
    
  def set_lights(self, left_signal, right_signal, hazard_signal):
    self.vehicle.set_lights(
      left_signal,
      right_signal,
      hazard_signal
    )
    
  def get_sensor_data(self):
    self.vehicle.sensors.poll()
    
  def get_state(self):
    return self.vehicle.sensors['state']
  
  def get_electrics(self):
    return self.vehicle.sensors['electrics']

class StopEventSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.stop_event = None
        return cls._instance

    def set_stop_event(self, new_value):
        self.stop_event = new_value
        
    def get_value(self):
      return self.stop_event.is_set()


class VehicleStateSingleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.longitudinal_vel = 0
            cls._instance.steering_tire_angle = 0
            cls._instance.heading_rate = 0
            cls._instance.manual_mode = True
            cls._instance.enable_left = False
            cls._instance.enable_right = False
            cls._instance.enable_hazard = False
            
        return cls._instance

    # longitudinal_vel
    def get_longitudinal_vel(self):
        return self.longitudinal_vel

    def set_longitudinal_vel(self, new_value):
        self.longitudinal_vel = new_value

    # steering_tire_angle
    def get_steering_tire_angle(self):
        return self.steering_tire_angle

    def set_steering_tire_angle(self, new_value):
        self.steering_tire_angle = new_value

    # heading_rate
    def get_heading_rate(self):
        return self.heading_rate

    def set_heading_rate(self, new_value):
        self.heading_rate = new_value

    # manual_mode
    def get_manual_mode(self):
        return self.manual_mode

    def set_manual_mode(self, new_value):
        self.manual_mode = new_value

    # enable_left
    def get_enable_left(self):
        return self.enable_left

    def set_enable_left(self, new_value):
        self.enable_left = new_value

    # enable_right
    def get_enable_right(self):
        return self.enable_right

    def set_enable_right(self, new_value):
        self.enable_right = new_value

    # enable_hazard
    def get_enable_hazard(self):
        return self.enable_hazard

    def set_enable_hazard(self, new_value):
        self.enable_hazard = new_value

