use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, geometry_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

use crate::msg::geometry_msgs as my_geometry_msgs;
use crate::msg::nav_msgs;

pub fn publish_gps (
  gps_publisher: Arc<Mutex<Publisher<'static>>>,
  x: f64,
  y: f64,
  z: f64,
) -> PyResult<()> {
  let mut publisher = gps_publisher.lock().unwrap();

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

  let mut pose = my_geometry_msgs::PoseWithCovariance {
    pose: geometry_msgs::Pose {
      position: geometry_msgs::Point {
        x: x,
        y: y,
        z: z,
      },
      orientation: geometry_msgs::Quaternion {
        x: 0.0,
        y: 0.0,
        z: 0.0,
        w: 1.0,
      },
    },
    covariance: vec![0.0; 36],
  };
  pose.covariance[0] = 2.0;
  pose.covariance[7] = 2.0;

  let twist = my_geometry_msgs::TwistWithCovariance {
    twist: geometry_msgs::Twist {
      linear: geometry_msgs::Vector3 {
        x: 0.0,
        y: 0.0,
        z: 0.0,
      },
      angular: geometry_msgs::Vector3 {
        x: 0.0,
        y: 0.0,
        z: 0.0,
      },
    },
    covariance: vec![0.0; 36],
  };

  let odometry = nav_msgs::Odometry {
    header: header,
    child_frame_id: "base_link".to_string(),
    pose: pose,
    twist: twist,
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&odometry, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}