use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use zenoh::Wait;
use zenoh::pubsub::Publisher;

pub fn publish_data(publisher: &Arc<Mutex<Publisher<'static>>>, encoded: Vec<u8>) -> PyResult<()> {
  publisher
    .lock()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?
    .put(encoded)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}
