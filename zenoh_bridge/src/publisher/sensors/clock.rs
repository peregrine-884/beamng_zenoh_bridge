use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

use pyo3::prelude::*;
use cdr::{CdrLe, Infinite};

use zenoh::pubsub::Publisher;

use zenoh_ros_type::{builtin_interfaces, rosgraph_msgs};


use crate::utils::create_publisher::create_publisher;
use crate::utils::publish_data::publish_data;


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
    let now = SystemTime::now()
      .duration_since(UNIX_EPOCH)
      .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Unable to get current time"))?;

    let clock_msgs = rosgraph_msgs::Clock {
      clock: builtin_interfaces::Time {
        sec: now.as_secs() as i32,
        nanosec: now.subsec_nanos(),
      },
    };

    let encoded = cdr::serialize::<_, _, CdrLe>(&clock_msgs, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

    publish_data(&self.publisher, encoded)
  }

}