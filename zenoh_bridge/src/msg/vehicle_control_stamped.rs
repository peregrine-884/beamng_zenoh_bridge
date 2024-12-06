use serde::{Deserialize, Serialize};
use zenoh_ros_type::{builtin_interfaces};

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct VehicleControl {
    pub stamp: builtin_interfaces::Time,
    pub throttle: f32,
    pub brake: f32,
    pub steering: f32,
}