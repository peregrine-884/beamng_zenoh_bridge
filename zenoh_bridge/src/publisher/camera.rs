use std::sync::{Arc, Mutex};
use pyo3::types::PyBytes;
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, sensor_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn publish_camera_data(
  camera_publisher: Arc<Mutex<Publisher<'static>>>, 
  data: &PyBytes
) -> PyResult<()> {
  let mut publisher = camera_publisher.lock().unwrap();

  let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .expect("Unable to get current time");

  let time = builtin_interfaces::Time {
    sec: now.as_secs() as i32,
    nanosec: now.subsec_nanos(),
  };

  let header = std_msgs::Header {
    stamp: time,
    frame_id: "camera".to_string(),
  };

  let data_slice: &[u8] = data.as_bytes();

  let width = 640_u32;
  let height = 480_u32;

  let image = sensor_msgs::Image {
    header: header,
    height: height,
    width: width,
    encoding: "rgb8".to_string(),
    is_bigendian: 0 as u8,
    step: width * 4 as u32,
    data: data_slice.to_vec(),
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&image, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}
