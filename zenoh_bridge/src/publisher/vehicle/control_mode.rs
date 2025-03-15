use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;
use zenoh_ros_type::autoware_vehicle_msgs;

use crate::utils::{create_stamp, create_publisher, publish_data};

#[pyclass]
pub struct ControlModePublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl ControlModePublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, control_mode: u8) -> PyResult<()> {
    let control_mode_msgs = autoware_vehicle_msgs::ControlModeReport { stamp: create_stamp(), mode: control_mode };

    publish_data(&self.publisher, &control_mode_msgs)
  }
}