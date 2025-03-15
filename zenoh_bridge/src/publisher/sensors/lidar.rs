use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use numpy::{PyArray2, PyArrayMethods}; 

use zenoh::pubsub::Publisher;

use zenoh_ros_type::sensor_msgs;

use crate::utils::{create_header, create_publisher, publish_data};

#[pyclass]
pub struct LidarDataPublisher {
  publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl LidarDataPublisher {
  #[new]
  fn new(config_path: &str, topic_name: &str) -> PyResult<Self> {
    let publisher = create_publisher(config_path, topic_name)?;

    Ok(Self { publisher })
  }

  fn publish(&self, frame_id: &str, data: &Bound<'_, PyArray2<f32>>) -> PyResult<()> {
    let header = create_header(frame_id);

    let points: Vec<f32> = unsafe {
      data
        .as_slice()
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid point cloud data"))?
        .to_vec()
    };

    let point_step = 16;
    let point_count = points.len() / 4;

    let data: Vec<u8> = points
      .chunks_exact(4)
      .flat_map(|chunk| {
        [
          chunk[0].to_ne_bytes(),
          chunk[1].to_ne_bytes(),
          chunk[2].to_ne_bytes(),
          chunk[3].to_ne_bytes(),
        ]
      })
      .flatten()
      .collect();

    let fields = vec![
      sensor_msgs::PointField {
        name: "x".to_string(),
        offset: 0,
        datatype: 7,
        count: 1,
      },
      sensor_msgs::PointField {
        name: "y".to_string(),
        offset: 4,
        datatype: 7,
        count: 1,
      },
      sensor_msgs::PointField {
        name: "z".to_string(),
        offset: 8,
        datatype: 7,
        count: 1,
      },
      sensor_msgs::PointField {
        name: "intensity".to_string(),
        offset: 12,
        datatype: 2,
        count: 1,
      },
      sensor_msgs::PointField {
        name: "return_type".to_string(),
        offset: 13,
        datatype: 2,
        count: 1,
      },
      sensor_msgs::PointField {
        name: "channel".to_string(),
        offset: 14,
        datatype: 4,
        count: 1,
      },
    ];

    let pointcloud2 = sensor_msgs::PointCloud2 {
      header,
      height: 1,
      width: point_count as u32,
      fields,
      is_bigendian: false,
      point_step,
      row_step: data.len() as u32,
      data,
      is_dense: false,
    };

    publish_data(&self.publisher, &pointcloud2)
  }

}