use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, sensor_msgs, geometry_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn publish_imu_data(
  imu_publisher: Arc<Mutex<Publisher<'static>>>,
  imu_data: Vec<f64>
) -> PyResult<()> {
  let mut publisher = imu_publisher.lock().unwrap();

  let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .expect("Unable to get current time");

  let time = builtin_interfaces::Time {
    sec: now.as_secs() as i32,
    nanosec: now.subsec_nanos(),
  };

  let header = std_msgs::Header {
    stamp: time,
    frame_id: "xsens_imu_link".to_string(),
  };

  let imu_msg = sensor_msgs::IMU {
    header: header,
    orientation: geometry_msgs::Quaternion {
      x: imu_data[0],
      y: imu_data[1],
      z: imu_data[2],
      w: imu_data[3],
    },
    orientation_covariance: [0.0; 9],
    angular_velocity: geometry_msgs::Vector3 {
      x: imu_data[4],
      y: imu_data[5],
      z: imu_data[6],
    },
    angular_velocity_covariance: [0.0; 9],
    linear_acceleration: geometry_msgs::Vector3 {
      x: imu_data[7],
      y: imu_data[8],
      z: imu_data[9],
    },
    linear_acceleration_covariance: [0.0; 9],
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&imu_msg, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}
