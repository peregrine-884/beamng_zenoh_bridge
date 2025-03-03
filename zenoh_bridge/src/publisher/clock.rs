use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, rosgraph_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn publish_clock_data(clock_publisher: Arc<Mutex<Publisher<'static>>>) -> PyResult<()> {
  let mut publisher = clock_publisher.lock().map_err(|e| {
    pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to lock publisher: {}", e))
  })?;

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

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}