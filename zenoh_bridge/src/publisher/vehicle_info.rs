use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, autoware_vehicle_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};

use crate::msg::tier4_vehicle_msgs;

fn get_current_time() -> builtin_interfaces::Time {
  let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .expect("Unable to get current time");
  builtin_interfaces::Time {
    sec: now.as_secs() as i32,
    nanosec: now.subsec_nanos(),
  }
}

fn publish_message<T: serde::Serialize>(
  publisher: &Arc<Mutex<Publisher<'static>>>,
  message: &T,
) -> PyResult<()> {
  let serialized = cdr::serialize::<_, _, CdrLe>(message, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
  publisher
    .lock().unwrap()
    .put(serialized)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}

pub fn publish_vehicle_info (
  velocity_publisher: Arc<Mutex<Publisher<'static>>>,
  steering_publisher: Arc<Mutex<Publisher<'static>>>,
  gear_publisher: Arc<Mutex<Publisher<'static>>>,
  control_mode_publisher: Arc<Mutex<Publisher<'static>>>,
  battery_publisher: Arc<Mutex<Publisher<'static>>>,
  hazard_publisher: Arc<Mutex<Publisher<'static>>>,
  turn_signal_publisher: Arc<Mutex<Publisher<'static>>>,
  longitudinal_vel: f32,
  lateral_vel: f32,
  heading_rate: f32,
  steering_tire_angle: f32,
  gear: u8,
  control_mode: u8,
  battery: f32,
  hazard: u8,
  turn_signal: u8,
) -> PyResult<()> {
  let time = get_current_time();
  let header = std_msgs::Header {
    stamp: time.clone(),
    frame_id: "base_link".to_string(),
  };

  let velocity_msg = autoware_vehicle_msgs::VelocityReport {
    header,
    longitudinal_velocity: if longitudinal_vel.abs() <= 0.1 { 0.0 } else { longitudinal_vel },
    lateral_velocity: lateral_vel,
    heading_rate,
  };
  publish_message(&velocity_publisher, &velocity_msg)?;

  let steering_msg = autoware_vehicle_msgs::SteeringReport {
    stamp: time.clone(),
    steering_tire_angle: if steering_tire_angle.abs() <= 0.01 { 0.0 } else { steering_tire_angle },
  };
  publish_message(&steering_publisher, &steering_msg)?;

  let gear_msg = autoware_vehicle_msgs::GearReport { stamp: time.clone(), report: gear };
  publish_message(&gear_publisher, &gear_msg)?;

  let control_mode_msg = autoware_vehicle_msgs::ControlModeReport { stamp: time.clone(), mode: control_mode };
  publish_message(&control_mode_publisher, &control_mode_msg)?;

  let battery_msg = tier4_vehicle_msgs::BatteryStatus { stamp: time.clone(), energy_level: battery };
  publish_message(&battery_publisher, &battery_msg)?;

  let hazard_msg = autoware_vehicle_msgs::HazardLightsReport { stamp: time.clone(), report: hazard };
  publish_message(&hazard_publisher, &hazard_msg)?;

  let turn_signal_msg = autoware_vehicle_msgs::TurnIndicatorsReport { stamp: time.clone(), report: turn_signal };
  publish_message(&turn_signal_publisher, &turn_signal_msg)?;

  Ok(())
}