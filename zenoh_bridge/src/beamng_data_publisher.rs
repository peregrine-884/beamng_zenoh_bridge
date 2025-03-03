use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use numpy::PyArray2;
use zenoh::{prelude::*, Config, Session};
use zenoh::pubsub::Publisher;

use crate::publisher::{camera, clock, imu, lidar, vehicle_control, vehicle_info, gps};

#[pyclass(module = "beamng_data_publisher")]
pub struct BeamngDataPublisher {
  session: Arc<Session>,
  camera_publisher: Arc<Mutex<Publisher<'static>>>,
  clock_publisher: Arc<Mutex<Publisher<'static>>>,
  imu_publisher: Arc<Mutex<Publisher<'static>>>,
  lidar_publisher: Arc<Mutex<Publisher<'static>>>,
  vehicle_control_publisher: Arc<Mutex<Publisher<'static>>>,
  battery_publisher: Arc<Mutex<Publisher<'static>>>,
  control_mode_publisher: Arc<Mutex<Publisher<'static>>>,
  gear_publisher: Arc<Mutex<Publisher<'static>>>,
  hazard_publisher: Arc<Mutex<Publisher<'static>>>,
  turn_signal_publisher: Arc<Mutex<Publisher<'static>>>,
  steering_publisher: Arc<Mutex<Publisher<'static>>>,
  velocity_publisher: Arc<Mutex<Publisher<'static>>>,
  gps_publisher: Arc<Mutex<Publisher<'static>>>,
}

impl BeamngDataPublisher {
  fn create_publisher(session: &Arc<Session>, topic: &str) -> PyResult<Arc<Mutex<Publisher<'static>>>> {
    let topic_owned = topic.to_string(); // Stringに変換
    session.declare_publisher(topic_owned)
      .wait()
      .map(|p| Arc::new(Mutex::new(p)))
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
  }  
}

#[pymethods]
impl BeamngDataPublisher {
  #[new]
  fn new() -> PyResult<Self> {
    let config = Config::from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    
    let session = Arc::new(zenoh::open(config).wait().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?);

    Ok(Self {
      session: session.clone(),
      camera_publisher: Self::create_publisher(&session, "sensing/camera")?,
      clock_publisher: Self::create_publisher(&session, "clock")?,
      imu_publisher: Self::create_publisher(&session, "imu/data")?,
      lidar_publisher: Self::create_publisher(&session, "sensing/lidar/concatenated/pointcloud")?,
      vehicle_control_publisher: Self::create_publisher(&session, "vehicle/status/actuation_status")?,
      battery_publisher: Self::create_publisher(&session, "vehicle/status/battery_charge")?,
      control_mode_publisher: Self::create_publisher(&session, "vehicle/status/control_mode")?,
      gear_publisher: Self::create_publisher(&session, "vehicle/status/gear_status")?,
      hazard_publisher: Self::create_publisher(&session, "vehicle/status/hazard_lights_status")?,
      turn_signal_publisher: Self::create_publisher(&session, "vehicle/status/turn_indicators_status")?,
      steering_publisher: Self::create_publisher(&session, "vehicle/status/steering_status")?,
      velocity_publisher: Self::create_publisher(&session, "vehicle/status/velocity_status")?,
      gps_publisher: Self::create_publisher(&session, "odometry/gpsz")?,
    })
  }

  fn publish_camera_data(&self, data: &PyBytes) -> PyResult<()> {
    camera::publish_camera_data(self.camera_publisher.clone(), data)
  }

  fn publish_clock_data(&self) -> PyResult<()> {
    clock::publish_clock_data(self.clock_publisher.clone())
  }

  fn publish_imu_data(&self, imu_data: Vec<f64>) -> PyResult<()> {
    imu::publish_imu_data(self.imu_publisher.clone(), imu_data)
  }

  fn publish_lidar_data(&self, pointcloud: &PyArray2<f32>, frame_id: &str) -> PyResult<()> {
    lidar::publish_lidar_data(self.lidar_publisher.clone(), pointcloud, frame_id)
  }

  fn publish_vehicle_control(&self, throttle: f32, brake: f32, steering: f32) -> PyResult<()> {
    vehicle_control::publish_vehicle_control(self.vehicle_control_publisher.clone(), throttle, brake, steering)
  }

  fn publish_vehicle_info(
    &self,
    longitudinal_vel: f32,
    lateral_vel: f32,
    heading_rate: f32,
    steering_tire_angle: f32,
    gear: u8,
    control_mode: u8,
    battery: f32,
    hazard: u8,
    turn_signal: u8,
  ) -> PyResult<()> {
    vehicle_info::publish_vehicle_info(
      self.velocity_publisher.clone(),
      self.steering_publisher.clone(),
      self.gear_publisher.clone(),
      self.control_mode_publisher.clone(),
      self.battery_publisher.clone(),
      self.hazard_publisher.clone(),
      self.turn_signal_publisher.clone(),
      longitudinal_vel,
      lateral_vel,
      heading_rate,
      steering_tire_angle,
      gear,
      control_mode,
      battery,
      hazard,
      turn_signal,
    )
  }

  fn publish_gps(&self, x: f64, y: f64, z: f64) -> PyResult<()> {
    gps::publish_gps(self.gps_publisher.clone(), x, y, z)
  }
}