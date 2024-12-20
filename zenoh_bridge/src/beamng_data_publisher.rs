use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use numpy::{PyArray2};
use zenoh::{prelude::*, Config, Session};
use zenoh::pubsub::Publisher;

use crate::publisher::camera;
use crate::publisher::clock;
use crate::publisher::imu;
use crate::publisher::lidar;
use crate::publisher::vehicle_control;
use crate::publisher::vehicle_info;
use crate::publisher::gps;

#[pyclass(module = "beamng_data_publisher")]
pub struct BeamngDataPublisher {
  pub session: Arc<Session>,
  pub camera_publisher: Arc<Mutex<Publisher<'static>>>,
  pub clock_publisher: Arc<Mutex<Publisher<'static>>>,
  pub imu_publisher: Arc<Mutex<Publisher<'static>>>,
  pub lidar_publisher: Arc<Mutex<Publisher<'static>>>,
  pub vehicle_control_publisher: Arc<Mutex<Publisher<'static>>>,
  pub battery_publisher: Arc<Mutex<Publisher<'static>>>,
  pub control_mode_publisher: Arc<Mutex<Publisher<'static>>>,
  pub gear_publisher: Arc<Mutex<Publisher<'static>>>,
  pub hazard_publisher: Arc<Mutex<Publisher<'static>>>,
  pub turn_signal_publisher: Arc<Mutex<Publisher<'static>>>,
  pub steering_publisher: Arc<Mutex<Publisher<'static>>>,
  pub velocity_publisher: Arc<Mutex<Publisher<'static>>>,
  pub gps_publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl BeamngDataPublisher {
  #[new]
  fn new() -> PyResult<Self> {
    let config = Config::from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
      .expect("Unable to load configuration");

    let session = zenoh::open(config).wait().expect("Unable to open session");
    let session = Arc::new(session);

    let camera_publisher = session
      .declare_publisher("sensing/camera")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let camera_publisher = Arc::new(Mutex::new(camera_publisher));

    let clock_publisher = session
      .declare_publisher("clock")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let clock_publisher = Arc::new(Mutex::new(clock_publisher));

    let imu_publisher = session
      .declare_publisher("imu/data")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let imu_publisher = Arc::new(Mutex::new(imu_publisher));

    let lidar_publisher = session
      .declare_publisher("sensing/lidar/concatenated/pointcloud")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let lidar_publisher = Arc::new(Mutex::new(lidar_publisher));

    let vehicle_control_publisher = session
      .declare_publisher("vehicle/status/actuation_status")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let vehicle_control_publisher = Arc::new(Mutex::new(vehicle_control_publisher));
        
    let battery_publisher = session
      .declare_publisher("vehicle/status/battery_charge")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let battery_publisher = Arc::new(Mutex::new(battery_publisher));

    let control_mode_publisher = session
      .declare_publisher("vehicle/status/control_mode")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let control_mode_publisher = Arc::new(Mutex::new(control_mode_publisher));

    let gear_publisher = session
      .declare_publisher("vehicle/status/gear_status")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let gear_publisher = Arc::new(Mutex::new(gear_publisher));

    let hazard_publisher = session
      .declare_publisher("vehicle/status/hazard_lights_status")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let hazard_publisher = Arc::new(Mutex::new(hazard_publisher));

    let turn_signal_publisher = session
      .declare_publisher("vehicle/status/turn_indicators_status")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let turn_signal_publisher = Arc::new(Mutex::new(turn_signal_publisher));

    let steering_publisher = session
      .declare_publisher("vehicle/status/steering_status")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let steering_publisher = Arc::new(Mutex::new(steering_publisher));

    let velocity_publisher = session
      .declare_publisher("vehicle/status/velocity_status")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let velocity_publisher = Arc::new(Mutex::new(velocity_publisher));

    let gps_publisher = session
      .declare_publisher("odometry/gpsz")
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let gps_publisher = Arc::new(Mutex::new(gps_publisher));

    Ok(BeamngDataPublisher {
      session,
      camera_publisher,
      clock_publisher,
      imu_publisher,
      lidar_publisher,
      vehicle_control_publisher,
      battery_publisher,
      control_mode_publisher,
      gear_publisher,
      hazard_publisher,
      turn_signal_publisher,
      steering_publisher,
      velocity_publisher,
      gps_publisher,
    })
  }

  fn publish_camera_data(&self, data: &PyBytes) -> PyResult<()> {
    camera::publish_camera_data(self.camera_publisher.clone(), data)
  }

  fn publish_clock_data(&self) ->PyResult<()> {
    clock::publish_clock_data(self.clock_publisher.clone())
  }

  fn publish_imu_data(&self, imu_data: Vec<f64>) -> PyResult<()> {
    imu::publish_imu_data(self.imu_publisher.clone(), imu_data)
  }

  fn publish_lidar_data(&self, pointcloud: &PyArray2<f32>) -> PyResult<()> {
    lidar::publish_lidar_data(self.lidar_publisher.clone(), pointcloud)
  }

  fn publish_vehicle_control(
    &self,
    throttle: f32,
    brake: f32,
    steering: f32,
  ) -> PyResult<()> {
    vehicle_control::publish_vehicle_control(
      self.vehicle_control_publisher.clone(),
      throttle,
      brake,
      steering,
    )
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

  fn publish_gps(
    &self,
    x: f64,
    y: f64,
    z: f64
  ) -> PyResult<()> {
    gps::publish_gps(self.gps_publisher.clone(), x, y, z)
  }
}