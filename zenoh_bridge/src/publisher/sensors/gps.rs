use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use cdr::{CdrLe, Infinite};

use zenoh::pubsub::Publisher;

use zenoh_ros_type::geometry_msgs;

use crate::msg::{geometry_msgs as my_geometry_msgs, nav_msgs};
use crate::utils::create_publisher::create_publisher;
use crate::utils::create_header::create_header;
use crate::utils::publish_data::publish_data;


#[pyclass]
pub struct GPSDataPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl GPSDataPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, frame_id: &str, x: f64, y: f64, z: f64) -> PyResult<()> {
    let header = create_header(frame_id);

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

    // Set GPS measurement error
    pose.covariance[0] = 2.0;
    pose.covariance[7] = 2.0;

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

    publish_data(&self.publisher, encoded)
  }

}