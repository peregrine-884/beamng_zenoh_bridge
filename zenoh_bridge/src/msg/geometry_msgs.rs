use serde_derive::{Deserialize, Serialize};
use zenoh_ros_type::{geometry_msgs};

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct PoseWithCovariance {
  pub pose: geometry_msgs::Pose,
  pub covariance: Vec<f64>,
}

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct TwistWithCovariance {
  pub twist: geometry_msgs::Twist,
  pub covariance: Vec<f64>,
}

