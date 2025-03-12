use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;
use zenoh_ros_type::autoware_vehicle_msgs;

use crate::utils::{create_header, create_publisher, publish_data};

#[pyclass]
pub struct VelocityStatusPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl VelocityStatusPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, frame_id: &str, longitudinal_vel: f32, lateral_vel: f32, heading_rate: f32) -> PyResult<()> {
    let header = create_header(frame_id);

    let velocity_msgs = autoware_vehicle_msgs::VelocityReport {
      header,
      longitudinal_velocity: if longitudinal_vel.abs() <= 0.1 { 0.0 } else { longitudinal_vel },
      lateral_velocity: lateral_vel,
      heading_rate,
    };

    publish_data(&self.publisher, &velocity_msgs)
  }
}