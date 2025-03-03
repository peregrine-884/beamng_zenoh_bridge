use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, sensor_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn publish_camera_data(
  camera_publisher: Arc<Mutex<Publisher<'static>>>, 
  data: &PyBytes
) -> PyResult<()> {
  let mut publisher = camera_publisher.lock().map_err(|e| {
    pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to lock publisher: {}", e))
  })?;

  let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Unable to get current time"))?;

  let header = std_msgs::Header {
    stamp: builtin_interfaces::Time {
      sec: now.as_secs() as i32,
      nanosec: now.subsec_nanos(),
    },
    frame_id: "camera".to_string(),
  };

  let width = 640_u32;
  let height = 480_u32;
  let encoding = "rgba8".to_string();
  let step = width * 4;

  let image = sensor_msgs::Image {
    header,
    height,
    width,
    encoding,
    is_bigendian: 0,
    step,
    data: data.as_bytes().to_vec(),
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&image, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}