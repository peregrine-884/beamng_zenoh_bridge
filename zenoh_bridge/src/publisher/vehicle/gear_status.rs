use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;
use zenoh_ros_type::autoware_vehicle_msgs;

use crate::utils::{create_stamp, create_publisher, publish_data};

#[pyclass]
pub struct GearStatusPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl GearStatusPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, gear: u8) -> PyResult<()> {
    let gear_msgs = autoware_vehicle_msgs::GearReport { stamp: create_stamp(), report: gear };

    publish_data(&self.publisher, &gear_msgs)
  }
}