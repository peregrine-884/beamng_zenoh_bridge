use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;

use crate::msg::tier4_vehicle_msgs;
use crate::utils::{create_stamp, create_publisher, publish_data};

#[pyclass]
pub struct BatteryChargePublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl BatteryChargePublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, battery: f32) -> PyResult<()> {
    let battery_msgs = tier4_vehicle_msgs::BatteryStatus { stamp: create_stamp(), energy_level: battery };

    publish_data(&self.publisher, &battery_msgs)
  }
}