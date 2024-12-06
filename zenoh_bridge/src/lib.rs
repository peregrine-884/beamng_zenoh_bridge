mod beamng_data_publisher;
mod publisher;
mod msg;

use pyo3::prelude::*;
use beamng_data_publisher::BeamngDataPublisher;

#[pymodule]
fn zenoh_bridge(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BeamngDataPublisher>()?;
    Ok(())
}