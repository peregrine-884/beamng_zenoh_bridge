use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::Wait;
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{builtin_interfaces, std_msgs, sensor_msgs};
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};
use numpy::PyArray2;

pub fn publish_lidar_data(
  lidar_publisher: Arc<Mutex<Publisher<'static>>>,
  pointcloud: &PyArray2<f32>,
  frame_id: &str,
) -> PyResult<()> {
  let mut publisher = lidar_publisher.lock().map_err(|e| {
    pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to lock publisher: {}", e))
  })?;

  let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Unable to get current time"))?;

  let header = std_msgs::Header {
    stamp: builtin_interfaces::Time {
      sec: now.as_secs() as i32,
      nanosec: now.subsec_nanos(),
    },
    frame_id: frame_id.to_string(),
  };

  let points: Vec<f32> = unsafe {
    pointcloud
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
    is_dense: true,
  };

  let encoded = cdr::serialize::<_, _, CdrLe>(&pointcloud2, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}