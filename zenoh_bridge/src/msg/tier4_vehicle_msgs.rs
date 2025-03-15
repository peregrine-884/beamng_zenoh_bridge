use serde_derive::{Deserialize, Serialize};
use zenoh_ros_type::{builtin_interfaces, std_msgs};

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct ActuationStatus {
  pub accel_status: f64,
  pub brake_status: f64,
  pub steer_status: f64
}

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct ActuationStatusStamped {
  pub header: std_msgs::Header,
  pub status: ActuationStatus
}

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct BatteryStatus {
    pub stamp: builtin_interfaces::Time,
    pub energy_level: f32,
}

