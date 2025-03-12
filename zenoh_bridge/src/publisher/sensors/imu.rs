use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use cdr::{CdrLe, Infinite};

use zenoh::pubsub::Publisher;

use zenoh_ros_type::{geometry_msgs, sensor_msgs};

use crate::utils::create_publisher::create_publisher;
use crate::utils::create_header::create_header;
use crate::utils::publish_data::publish_data;


#[pyclass]
pub struct IMUDataPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl IMUDataPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, data: Vec<f64>, frame_id: &str) -> PyResult<()> {
    let header = create_header(frame_id);

    let imu_msgs = sensor_msgs::IMU {
      header,
      orientation: geometry_msgs::Quaternion {
        x: data[0],
        y: data[1],
        z: data[2],
        w: data[3],
      },
      orientation_covariance: [0.0; 9],
      angular_velocity: geometry_msgs::Vector3 {
        x: data[4],
        y: data[5],
        z: data[6],
      },
      angular_velocity_covariance: [0.0; 9],
      linear_acceleration: geometry_msgs::Vector3 {
        x: data[7],
        y: data[8],
        z: data[9],
      },
      linear_acceleration_covariance: [0.0; 9],
    };

    let encoded = cdr::serialize::<_, _, CdrLe>(&imu_msgs, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;


    publish_data(&self.publisher, encoded)
  }
}