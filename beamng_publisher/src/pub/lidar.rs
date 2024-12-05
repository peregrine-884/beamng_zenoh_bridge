use pyo3::prelude::*;
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};
use numpy::{PyArray2};
use zenoh_ros_type::{
  builtin_interfaces,
  std_msgs,
  sensor_msgs,
};

#[pymethods]
impl BeamngDataPublisher {
  fn publish_lidar_data(&self, pointcloud: &PyArray2<f32>) -> PyResult<()> {
    let mut publisher = self.lidar_publisher.lock().unwrap();

    let now = SystemTime::now()
      .duration_since(UNIX_EPOCH)
      .expect("Unable to get current time");

    let time = builtin_interfaces::Time {
        sec: now.as_secs() as i32,
        nanosec: now.subsec_nanos(),
    };

    let header = std_msgs::Header {
        stamp: time,
        frame_id: "base_link".to_string()
    };

    let points: Vec<f32> = unsafe {
      pointcloud.as_slice().unwrap().to_vec()
    };

    let point_step = 16 as u32;

    let point_count = points.len() as u32 / 4;

    let data: Vec<u8> = (0..point_count)
      .flap_map(|i| {
        let x = points[i * 4 + 0];
        let y = points[i * 4 + 1];
        let z = points[i * 4 + 2];
        let intensity = points[i * 4 + 3];

        [
          x.to_ne_bytes(),
          y.to_ne_bytes(),
          z.to_ne_bytes(),
          intensity.to_ne_bytes(),
        ]
      })
      .flap_map(|elem| elem)
      .collect();

    let row_step = data.len() as u32;

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

    let pointcloud2 = sensor_msgs::Pointcloud2 {
      header,
      height: 1,
      width: point_count as u32,
      fields,
      is_bigendian: false,
      point_step,
      row_step,
      data,
      is_dencse: true,
    };

    let encoded = cdr::serialize::<_, _, CdrLe>(&pointcloud2, Infinite)
      .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

    publisher
      .put(encoded)
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    Ok(())
  }
}