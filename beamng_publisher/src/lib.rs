use pyo3::prelude::*;
use pyo3::types::PyBytes;
use cdr::{CdrLe, Infinite};
use std::time::{SystemTime, UNIX_EPOCH};
use zenoh::{prelude::*, Config, Session};
use zenoh::pubsub::Publisher;
use zenoh_ros_type::{
    builtin_interfaces,
    std_msgs,
    sensor_msgs,
    geometry_msgs,
    autoware_vehicle_msgs,
    rosgraph_msgs
};
use numpy::{PyArray2};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct BatteryStatus {
    pub stamp: builtin_interfaces::Time,
    pub energy_level: f32,
}

#[derive(Serialize, Deserialize, PartialEq, Clone)]
pub struct VehicleControl {
    pub stamp: builtin_interfaces::Time,
    pub throttle: f32,
    pub brake: f32,
    pub steering: f32,
}

#[pyclass(module = "beamng_publisher")]
pub struct BeamngPublisher {
    session: Arc<Session>,
    
    
    
    
    

}

#[pymethods]
impl BeamngPublisher {
}

#[pymodule]
fn beamng_publisher(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BeamngPublisher>()?;
    Ok(())
}
