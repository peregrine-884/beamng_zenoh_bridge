use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, geometry_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

use crate::msg::{geometry_msgs as my_geometry_msgs, nav_msgs};

pub fn publish_gps(
  gps_publisher: Arc<Mutex<Publisher<'static>>>,
  x: f64,
  y: f64,
  z: f64,
) -> PyResult<()> {
  let mut publisher = gps_publisher.lock().map_err(|e| {
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
    frame_id: "base_link".to_string(),
  };

  let mut pose = my_geometry_msgs::PoseWithCovariance {
    pose: geometry_msgs::Pose {
      position: geometry_msgs::Point { x, y, z },
      orientation: geometry_msgs::Quaternion {
        x: 0.0,
        y: 0.0,
        z: 0.0,
        w: 1.0,
      },
    },
    covariance: vec![0.0; 36],
  };

  // GPS測定誤差の設定
  pose.covariance[0] = 2.0;  // X方向の誤差
  pose.covariance[7] = 2.0;  // Y方向の誤差

  let twist = my_geometry_msgs::TwistWithCovariance {
    twist: geometry_msgs::Twist {
      linear: geometry_msgs::Vector3 { x: 0.0, y: 0.0, z: 0.0 },
      angular: geometry_msgs::Vector3 { x: 0.0, y: 0.0, z: 0.0 },
    },
    covariance: vec![0.0; 36],
  };

  let odometry = nav_msgs::Odometry {
    header,
    child_frame_id: "base_link".to_string(),
    pose,
    twist,
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&odometry, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}