mod msg;
mod publisher;
mod utils;

use pyo3::prelude::*;
use pyo3::types::PyModule;

use publisher::sensors::{
    CameraDataPublisher,
    ClockDataPublisher,
    GPSDataPublisher,
    IMUDataPublisher,
    LidarDataPublisher
};

use publisher::vehicle::{
    ActuationStatusPublisher,
    BatteryChargePublisher,
    ControlModePublisher,
    GearStatusPublisher,
    HazardLightsStatusPublisher,
    SteeringStatusPublisher,
    TurnIndicatorsStatusPublisher,
    VelocityStatusPublisher
};

#[pymodule]
fn zenoh_bridge(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Sensors
    m.add_class::<CameraDataPublisher>()?;
    m.add_class::<ClockDataPublisher>()?;
    m.add_class::<GPSDataPublisher>()?;
    m.add_class::<IMUDataPublisher>()?;
    m.add_class::<LidarDataPublisher>()?;

    // Vehicle
    m.add_class::<ActuationStatusPublisher>()?;
    m.add_class::<BatteryChargePublisher>()?;
    m.add_class::<ControlModePublisher>()?;
    m.add_class::<GearStatusPublisher>()?;
    m.add_class::<HazardLightsStatusPublisher>()?;
    m.add_class::<SteeringStatusPublisher>()?;
    m.add_class::<TurnIndicatorsStatusPublisher>()?;
    m.add_class::<VelocityStatusPublisher>()?;

    Ok(())
}