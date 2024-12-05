use pyo3::prelude::*;
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};
use zenoh_ros_type::{
  builtin_interfaces,
  std_msgs,
  autoware_vehicle_msgs,
};

#[pymethods]
impl BeamngDataPublisher {
  fn publish_vehicle_info (
    &self,
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
    let mut velocity_pub = self.velocity_publisher.lock().unwrap();
    let velocity_msgs = {
      let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Unable to get current time");
      let time = builtin_interfaces::Time {
        sec: now.as_secs() as i32,
        nanosec: now.subsec_nanos(),
      };
      let header = std_msgs::Header {
        stamp: time.clone(),
        frame_id: "base_link".to_string(),
      };

      let longitudinal_velocity = if longitudinal_vel >= -0.1 && longitudinal_vel <= 0.1 {
        0.0
      } else {
        longitudinal_vel
      };

      autoware_vehicle_msgs::VelocityReport {
        header: header,
        longitudinal_velocity: longitudinal_velocity,
        lateral_velocity: lateral_vel,
        heading_rate: heading_rate,
      }
    };
    let serialized_velocity = cdr::serialize::<_, _, CdrLe>(&velocity_msgs, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
    velocity_pub
      .put(serialized_velocity)
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let mut steering_pub = self.steering_publisher.lock().unwrap();
    let steering_msgs = {
      let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Unable to get current time");
      let time = builtin_interfaces::Time {
        sec: now.as_secs() as i32,
        nanosec: now.subsec_nanos(),
      };

      let steerring_angle = if steering_tire_angle >= -0.01 && steering_tire_angle <= 0.01 {
        0.0
      } else {
        steering_tire_angle
      };

      autoware_vehicle_msgs::SteeringReport {
        stamp: time.clone(),
        steering_wheel_angle: steering_tire_angle,
      }
    };
    let serialized_steering = cdr::serialize::<_, _, CdrLe>(&steering_msgs, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
    steering_pub
      .put(serialized_steering)
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let mut gear_pub = self.gear_publisher.lock().unwrap();
    let gear_msgs = {
      let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Unable to get current time");
      let time = builtin_interfaces::Time {
        sec: now.as_secs() as i32,
        nanosec: now.subsec_nanos(),
      };

      autoware_vehicle_msgs::GearReport {
        stamp: time.clone(),
        gear: gear,
      }
    };
    let serialized_gear = cdr::serialize::<_, _, CdrLe>(&gear_msgs, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
    gear_pub
      .put(serialized_gear)
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let mut control_mode_pub = self.control_mode_publisher.lock().unwrap();
    let control_mode_msgs = {
      let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Unable to get current time");
      let time = builtin_interfaces::Time {
        sec: now.as_secs() as i32,
        nanosec: now.subsec_nanos(),
      };

      autoware_vehicle_msgs::ControlModeReport {
        stamp: time.clone(),
        mode: control_mode,
      }
    };
    let serialized_control_mode = cdr::serialize::<_, _, CdrLe>(&control_mode_msgs, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
    control_mode_pub
      .put(serialized_control_mode)
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    // let mut battery_pub = self.battery_publisher.lock().unwrap();
    // let battery_msgs = {
    //   let now = SystemTime::now()
    //     .duration_since(UNIX_EPOCH)
    //     .expect("Unable to get current time");
    //   let time = builtin_interfaces::Time {
    //     sec: now.as_secs() as i32,
    //     nanosec: now.subsec_nanos(),
    //   };

    //   autoware_vehicle_msgs::BatteryReport {
    //     stamp: time.clone(),
    //     energy_level: battery,
    //   }
    // };
    // let serialized_battery = cdr::serialize::<_, _, CdrLe>(&battery_msgs, Infinite)
    //   .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
    // battery_pub
    //   .put(serialized_battery)
    //   .wait()
    //   .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    // let mut hazard_pub = self.hazard_publisher.lock().unwrap();
    // let hazard_msgs = {
    //   let now = SystemTime::now()
    //     .duration_since(UNIX_EPOCH)
    //     .expect("Unable to get current time");
    //   let time = builtin_interfaces::Time {
    //     sec: now.as_secs() as i32,
    //     nanosec: now.subsec_nanos(),
    //   };

    //   autoware_vehicle_msgs::HazardLightsReport {
    //     stamp: time.clone(),
    //     report: hazard,
    //   }
    // };
    // let serialized_hazard = cdr::serialize::<_, _, CdrLe>(&hazard_msgs, Infinite)
    //   .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
    // hazard_pub
    //   .put(serialized_hazard)
    //   .wait()
    //   .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    // let mut turn_signal_pub = self.turn_signal_publisher.lock().unwrap();
    // let turn_signal_msgs = {
    //   let now = SystemTime::now()
    //     .duration_since(UNIX_EPOCH)
    //     .expect("Unable to get current time");
    //   let time = builtin_interfaces::Time {
    //     sec: now.as_secs() as i32,
    //     nanosec: now.subsec_nanos(),
    //   };

    //   autoware_vehicle_msgs::TurnIndicatorsReport {
    //     stamp: time.clone(),
    //     report: turn_signal,
    //   }
    // };
    // let serialized_turn_signal = cdr::serialize::<_, _, CdrLe>(&turn_signal_msgs, Infinite)
    //   .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
    // turn_signal_pub
    //   .put(serialized_turn_signal)
    //   .wait()
    //   .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    Ok(())
  }
}