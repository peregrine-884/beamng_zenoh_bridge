use serde_derive::{Deserialize, Serialize};
use zenoh_ros_type::{std_msgs};

use crate::msg::geometry_msgs;

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct Odometry {
  pub header: std_msgs::Header,
  pub child_frame_id: String,
  pub pose: geometry_msgs::PoseWithCovariance,
  pub twist: geometry_msgs::TwistWithCovariance,
}