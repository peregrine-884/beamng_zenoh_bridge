use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::{prelude::*, Config, Session};
use zenoh::pubsub::Publisher;

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
      .declare_publisher("vehicle_control")
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
    })
  }
}