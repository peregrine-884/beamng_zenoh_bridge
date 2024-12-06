use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

use crate::msg::vehicle_control_stamped;

pub fn publish_vehicle_control(
  vehicle_control_publisher: Arc<Mutex<Publisher<'static>>>,
  throttle: f32,
  brake: f32,
  steering: f32,
) -> PyResult<()> {
  let mut publisher = vehicle_control_publisher.lock().unwrap();

  let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .expect("Unable to get current time");

  let time = builtin_interfaces::Time {
    sec: now.as_secs() as i32,
    nanosec: now.subsec_nanos(),
  };

  let vehicle_control = vehicle_control_stamped::VehicleControl {
    stamp: time,
    throttle: throttle,
    brake: brake,
    steering: steering,
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&vehicle_control, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}
