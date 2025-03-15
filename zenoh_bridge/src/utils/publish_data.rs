use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use cdr::{CdrLe, Infinite};

use zenoh::Wait;
use zenoh::pubsub::Publisher;

pub fn publish_data<T: serde::Serialize>
(publisher: &Arc<Mutex<Publisher<'static>>>, message: &T) -> PyResult<()> {
  let serialized = cdr::serialize::<_, _, CdrLe>(message, Infinite)
    .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

  publisher
    .lock()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?
    .put(serialized)
    .wait()
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

  Ok(())
}
