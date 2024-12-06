use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, rosgraph_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn publish_clock_data(
  clock_publisher: Arc<Mutex<Publisher<'static>>>
) -> PyResult<()> {
  let mut publisher = clock_publisher.lock().unwrap();

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

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}