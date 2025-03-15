use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;

use crate::utils::{create_stamp, create_publisher, publish_data};

#[pyclass]
pub struct ClockDataPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl ClockDataPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self) -> PyResult<()> {
    let clock_msgs = create_stamp();

    publish_data(&self.publisher, &clock_msgs)
  }

}