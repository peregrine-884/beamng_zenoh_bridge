use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use zenoh::pubsub::Publisher;

use zenoh_ros_type::sensor_msgs;

use crate::utils::{create_header, create_publisher, publish_data};

#[pyclass]
pub struct CameraDataPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl CameraDataPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, frame_id: &str, data: &Bound<'_, PyBytes>, width: f32, height: f32) -> PyResult<()> {
    let header = create_header(frame_id);

    let width = width as u32;
    let height = height as u32;
    let encoding = "rgba8".to_string();
    let step = width * 4;

    let image = sensor_msgs::Image {
      header,
      height,
      width,
      encoding,
      is_bigendian: 0,
      step,
      data: data.as_bytes().to_vec(),
    };

    publish_data(&self.publisher, &image)
  }
}