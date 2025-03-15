use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;

use crate::msg::tier4_vehicle_msgs;
use crate::utils::{create_header, create_publisher, publish_data};

#[pyclass]
pub struct ActuationStatusPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl ActuationStatusPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, frame_id: &str, throttle: f32, brake: f32, steering: f32) -> PyResult<()> {
    let header = create_header(frame_id);

    let actuation_status = tier4_vehicle_msgs::ActuationStatusStamped {
      header,
      status: tier4_vehicle_msgs::ActuationStatus {
        accel_status: throttle as f64,
        brake_status: brake as f64,
        steer_status: steering as f64,
      },
    };

    publish_data(&self.publisher, &actuation_status)
  }
}