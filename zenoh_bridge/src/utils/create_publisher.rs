use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use zenoh::{prelude::*, Config};
use zenoh::pubsub::Publisher;

pub fn create_publisher(config_path: &str, topic_name: &str) -> PyResult<Arc<Mutex<Publisher<'static>>>> {
  let config = Config::from_file(config_path)
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  let session = Arc::new(
    zenoh::open(config)
      .wait()
      .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?,
  );

  let publisher = session.declare_publisher(topic_name.to_string())
    .wait()
    .map(|p| Arc::new(Mutex::new(p)))
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(publisher)
}
