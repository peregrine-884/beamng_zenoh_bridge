use pyo3::prelude::*;
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};
use zenoh_ros_type::{
  builtin_interfaces,
  rosgraph_msgs
};

#[pymethods]
impl BeamngDataPublisher {
  fn publish_clock_data(&self) -> PyResult<()> {
    let mut publisher = self.clock_publisher.lock().unwrap();

    let now = SystemTime::now()
      .duration_since(UNIX_EPOCH)
      .expect("Unable to get current time");

    let time = builtin_interfaces::Time {
      sec: now.as_secs() as i32,
      nanosec: now.subsec_nanos(),
    };

    let clock_msgs = rosgraph_msgs::Clock {
      clock: time,
    };

    let encoded = cdr::serialize::<_, _, CdrLe>(&clock_msgs, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

    pubisher
      .put(encoded)
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    Ok(())
  }
}