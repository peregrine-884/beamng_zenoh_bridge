use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, sensor_msgs, geometry_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn publish_imu_data(
  imu_publisher: Arc<Mutex<Publisher<'static>>>,
  imu_data: Vec<f64>,
) -> PyResult<()> {
  if imu_data.len() < 10 {
    return Err(pyo3::exceptions::PyValueError::new_err(
      "imu_data must contain at least 10 elements",
    ));
  }

  let mut publisher = imu_publisher.lock().map_err(|e| {
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
    frame_id: "xsens_imu_link".to_string(),
  };

  let imu_msg = sensor_msgs::IMU {
    header,
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