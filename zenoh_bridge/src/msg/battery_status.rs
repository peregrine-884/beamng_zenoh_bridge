use serde::{Deserialize, Serialize};
use zenoh_ros_type::{builtin_interfaces};

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct BatteryStatus {
    pub stamp: builtin_interfaces::Time,
    pub energy_level: f32,
}