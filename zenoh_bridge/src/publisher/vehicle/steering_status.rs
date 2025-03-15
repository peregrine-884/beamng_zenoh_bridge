use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::pubsub::Publisher;
use zenoh_ros_type::autoware_vehicle_msgs;

use crate::utils::{create_stamp, create_publisher, publish_data};

#[pyclass]
pub struct SteeringStatusPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl SteeringStatusPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, steering_tire_angle: f32) -> PyResult<()> {
    let steering_msgs = autoware_vehicle_msgs::SteeringReport { 
      stamp: create_stamp(), 
      steering_tire_angle: if steering_tire_angle.abs() <= 0.01 {0.0} else {steering_tire_angle}, 
    };

    publish_data(&self.publisher, &steering_msgs)
  }
}