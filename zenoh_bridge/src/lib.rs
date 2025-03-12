mod msg;
mod publisher;
mod utils;

use pyo3::prelude::*;
use pyo3::types::PyModule;

use publisher::sensors::lidar::LidarDataPublisher;
use publisher::sensors::imu::IMUDataPublisher;

#[pymodule]
fn zenoh_bridge(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LidarDataPublisher>()?;
    m.add_class::<IMUDataPublisher>()?;
    Ok(())
}