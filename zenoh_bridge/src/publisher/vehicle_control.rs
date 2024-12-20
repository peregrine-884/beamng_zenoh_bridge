use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

use crate::msg::tier4_vehicle_msgs;

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

  let header = std_msgs::Header {
    stamp: time,
    frame_id: "base_link".to_string(),
  };

  let status = tier4_vehicle_msgs::ActuationStatus {
    accel_status: throttle as f64,
    brake_status: brake as f64,
    steer_status: steering as f64,
  };

  let actuation_status = tier4_vehicle_msgs::ActuationStatusStamped {
    header: header,
    status: status,
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&actuation_status, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}
