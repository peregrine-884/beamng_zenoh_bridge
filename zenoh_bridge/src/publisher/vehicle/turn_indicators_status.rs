use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;
use zenoh_ros_type::autoware_vehicle_msgs;

use crate::utils::{create_stamp, create_publisher, publish_data};

#[pyclass]
pub struct TurnIndicatorsStatusPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl TurnIndicatorsStatusPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, turn_signal: u8) -> PyResult<()> {
    let turn_signal_msgs = autoware_vehicle_msgs::TurnIndicatorsReport { stamp: create_stamp(), report: turn_signal };

    publish_data(&self.publisher, &turn_signal_msgs)
  }
}