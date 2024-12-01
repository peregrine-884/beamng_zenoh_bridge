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
    clock_publisher: Arc<Mutex<Publisher<'static>>>,
    pointcloud_publisher: Arc<Mutex<Publisher<'static>>>,
    imu_publisher: Arc<Mutex<Publisher<'static>>>,
    camera_publisher: Arc<Mutex<Publisher<'static>>>,
    velocity_publisher: Arc<Mutex<Publisher<'static>>>,
    steering_publisher: Arc<Mutex<Publisher<'static>>>,
    gear_publisher: Arc<Mutex<Publisher<'static>>>,
    control_mode_publisher: Arc<Mutex<Publisher<'static>>>,
    battery_publisher: Arc<Mutex<Publisher<'static>>>,
    hazard_publisher: Arc<Mutex<Publisher<'static>>>,
    turn_signal_publisher: Arc<Mutex<Publisher<'static>>>,
    vehicle_control_publisher: Arc<Mutex<Publisher<'static>>>,
}

#[pymethods]
impl BeamngPublisher {
    #[new]
    fn new() -> PyResult<Self> {
        let config = Config::from_file("C:\\Users\\hayat\\zenoh_beamng_bridge\\config\\beamng-conf.json5")
            .expect("Unable to load configuration");
        
        let session = zenoh::open(config).wait().expect("Unable to open session");
        let session = Arc::new(session);

        let clock_publisher = session
            .declare_publisher("clock")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let clock_publisher = Arc::new(Mutex::new(clock_publisher));

        let pointcloud_publisher = session
            .declare_publisher("sensing/lidar/concatenated/pointcloud")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let pointcloud_publisher = Arc::new(Mutex::new(pointcloud_publisher));

        let imu_publisher = session
            .declare_publisher("imu/data")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let imu_publisher = Arc::new(Mutex::new(imu_publisher));

        let camera_publisher = session
            .declare_publisher("sensing/camera")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let camera_publisher = Arc::new(Mutex::new(camera_publisher));

        let velocity_publisher = session
            .declare_publisher("vehicle/status/velocity_status")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let velocity_publisher = Arc::new(Mutex::new(velocity_publisher));

        let steering_publisher = session
            .declare_publisher("vehicle/status/steering_status")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let steering_publisher = Arc::new(Mutex::new(steering_publisher));

        let gear_publisher = session
            .declare_publisher("vehicle/status/gear_status")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let gear_publisher = Arc::new(Mutex::new(gear_publisher));

        let control_mode_publisher = session
            .declare_publisher("vehicle/status/control_mode")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let control_mode_publisher = Arc::new(Mutex::new(control_mode_publisher));

        let battery_publisher = session
            .declare_publisher("vehicle/status/battery_charge")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let battery_publisher = Arc::new(Mutex::new(battery_publisher));

        let hazard_publisher = session
            .declare_publisher("vehicle/status/hazard_lights_status")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let hazard_publisher = Arc::new(Mutex::new(hazard_publisher));

        let turn_signal_publisher = session
            .declare_publisher("vehicle/status/turn_indicators_status")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let turn_signal_publisher = Arc::new(Mutex::new(turn_signal_publisher));

        let vehicle_control_publisher = session
            .declare_publisher("vehicle_control")
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let vehicle_control_publisher = Arc::new(Mutex::new(vehicle_control_publisher));
        
        Ok(BeamngPublisher {
            session,
            clock_publisher,
            pointcloud_publisher,
            imu_publisher,
            camera_publisher,
            velocity_publisher,
            steering_publisher,
            gear_publisher,
            control_mode_publisher,
            battery_publisher,
            hazard_publisher,
            turn_signal_publisher,
            vehicle_control_publisher
        })
    }

    fn publish_clock(&self) -> PyResult<()> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Unable to get current time");

        let time = builtin_interfaces::Time {
            sec: now.as_secs() as i32,
            nanosec: now.subsec_nanos(),
        };

        let clock_msgs = rosgraph_msgs::Clock { clock: time };
        let encoded = cdr::serialize::<_, _, CdrLe>(&clock_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

        let mut publisher = self.clock_publisher.lock().unwrap();

        publisher
            .put(encoded)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        Ok(())
    }

    fn process_pointcloud(&self, pointcloud: &PyArray2<f32>) -> PyResult<()> {  
        let mut publisher = self.pointcloud_publisher.lock().unwrap();
    
        let points: Vec<f32> = unsafe {
            pointcloud.as_slice().unwrap().to_vec()
        };

        let point_step = 16 as u32;

        let point_count = points.len() / 4;
        // println!("Pointcloud length: {}", point_count);
        // println!("First 10 points:");
        // for i in 0..10.min(point_count) {
        //     let x = points[i * 4 + 0];
        //     let y = points[i * 4 + 1];
        //     let z = points[i * 4 + 2];
        //     let intensity = points[i * 4 + 3];
        //     println!("Point {}: x={}, y={}, z={}, intensity={}", i, x, y, z, intensity);
        // }

        let data: Vec<u8> = (0..point_count)
            .flat_map(|i| {
                let x = points[i * 4 + 0];
                let y = points[i * 4 + 1];
                let z = points[i * 4 + 2];
                let intensity = points[i * 4 + 3];

                [
                    x.to_ne_bytes(),
                    y.to_ne_bytes(),
                    z.to_ne_bytes(),
                    intensity.to_ne_bytes()
                ]
            })
            .flat_map(|elem| elem)
            .collect();

        let row_step = data.len() as u32;
    
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

        // let header = std_msgs::Header {
        //     stamp: time,
        //     frame_id: "velodyne_top".to_string()
        // };
    
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
            row_step,
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

    fn process_imu(&self, imu_data: Vec<f64>) -> PyResult<()> {
        let mut publisher = self.imu_publisher.lock().unwrap();

        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("UNable to get current time");

        let time = builtin_interfaces::Time {
            sec: now.as_secs() as i32,
            nanosec: now.subsec_nanos(),
        };

        let header = std_msgs::Header {
            stamp: time,
            frame_id: "xsens_imu_link".to_string()
        };

        let imu_msg = sensor_msgs::IMU {
            header: header,
            orientation: geometry_msgs::Quaternion {
                x: imu_data[0],
                y: imu_data[1],
                z: imu_data[2],
                w: imu_data[3]
            },
            orientation_covariance: [0.0; 9],
            angular_velocity: geometry_msgs::Vector3 {
                x: imu_data[4],
                y: imu_data[5],
                z: imu_data[6]
            },
            angular_velocity_covariance: [0.0; 9],
            linear_acceleration: geometry_msgs::Vector3 {
                x: imu_data[7],
                y: imu_data[8],
                z: imu_data[9]
            },
            linear_acceleration_covariance: [0.0; 9]
        };

        let encoded = cdr::serialize::<_, _, CdrLe>(&imu_msg, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

        publisher
            .put(encoded)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        Ok(())
    }

    fn process_camera(&self, data: &PyBytes) -> PyResult<()> {
        let mut publisher = self.camera_publisher.lock().unwrap();

        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("UNable to get current time");

        let time = builtin_interfaces::Time {
            sec: now.as_secs() as i32,
            nanosec: now.subsec_nanos(),
        };

        let header = std_msgs::Header {
            stamp: time,
            frame_id: "camera".to_string()
        };

        let data_slice: &[u8] = data.as_bytes();

        let width = 640_u32;
        let height = 480_u32;

        let image = sensor_msgs::Image {
            header: header,
            height: height,
            width: width,
            encoding: "rgba8".to_string(),
            is_bigendian: 0 as u8,
            step: width * 4 as u32,
            data: data_slice.to_vec()
        };

        let encoded = cdr::serialize::<_, _, CdrLe>(&image, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

        publisher
            .put(encoded)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        Ok(())
    }

    fn process_vehicle_control(
        &self,
        throttle: f32,
        brake: f32,
        steering: f32,
    ) -> PyResult<()> {
        println!("Throttle: {}, Brake: {}, Steering: {}", throttle, brake, steering);
        
        let mut publisher = self.vehicle_control_publisher.lock().unwrap();

        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Unable to get current time");

        let time = builtin_interfaces::Time {
            sec: now.as_secs() as i32,
            nanosec: now.subsec_nanos(),
        };

        let vehicle_control = VehicleControl {
            stamp: time,
            throttle: throttle,
            brake: brake,
            steering: steering,
        };

        let encoded = cdr::serialize::<_, _, CdrLe>(&vehicle_control, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;

        publisher
            .put(encoded)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        Ok(())
    }

    fn process_vehicle_status(
        &self,
        longitudinal_vel: f32,
        lateral_vel: f32,
        heading_rate: f32,
        steering_tire_angle: f32,
        gear: u8,
        control_mode: u8,
        battery: f32,
        hazard: u8,
        turn_signal: u8,
    ) -> PyResult<()> {
        let mut velocity_pub = self.velocity_publisher.lock().unwrap();
        let velocity_msgs = {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("Unable to get current time");
            let time = builtin_interfaces::Time {
                sec: now.as_secs() as i32,
                nanosec: now.subsec_nanos(),
            };
            let header = std_msgs::Header {
                stamp: time.clone(),
                frame_id: "base_link".to_string(),
            };

            let longitudinal_velocity = if longitudinal_vel >= -0.1 && longitudinal_vel <= 0.1 {
                0.0
            } else {
                longitudinal_vel
            };
    
            autoware_vehicle_msgs::VelocityReport {
                header: header,
                longitudinal_velocity: longitudinal_velocity,
                lateral_velocity: lateral_vel,
                heading_rate: heading_rate,
            }
        };
        let serialized_velocity = cdr::serialize::<_, _, CdrLe>(&velocity_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
        velocity_pub
            .put(serialized_velocity)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let mut steering_pub = self.steering_publisher.lock().unwrap();
        let steering_msgs = {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("Unable to get current time");
            let time = builtin_interfaces::Time {
                sec: now.as_secs() as i32,
                nanosec: now.subsec_nanos(),
            };

            let steering_angle = if steering_tire_angle >= -0.01 && steering_tire_angle <= 0.01 {
                0.0
            } else {
                steering_tire_angle
            };

            autoware_vehicle_msgs::SteeringReport {
                stamp: time.clone(),
                steering_tire_angle: steering_angle,
            }
        };
        let serialized_steering = cdr::serialize::<_, _, CdrLe>(&steering_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
        steering_pub
            .put(serialized_steering)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        

        let mut gear_pub = self.gear_publisher.lock().unwrap();
        let gear_msgs = {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("Unable to get current time");
            let time = builtin_interfaces::Time {
                sec: now.as_secs() as i32,
                nanosec: now.subsec_nanos(),
            };
            autoware_vehicle_msgs::GearReport {
                stamp: time.clone(),
                report: gear,
            }
        };
        let serialized_gear = cdr::serialize::<_, _, CdrLe>(&gear_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
        gear_pub
            .put(serialized_gear)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let mut control_mode_pub = self.control_mode_publisher.lock().unwrap();
        let control_mode_msgs = {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("Unable to get current time");
            let time = builtin_interfaces::Time {
                sec: now.as_secs() as i32,
                nanosec: now.subsec_nanos(),
            };
            autoware_vehicle_msgs::ControlModeReport {
                stamp: time.clone(),
                mode: control_mode,
            }
        };
        let serialized_control_mode = cdr::serialize::<_, _, CdrLe>(&control_mode_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
        control_mode_pub
            .put(serialized_control_mode)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let mut battery_pub = self.battery_publisher.lock().unwrap();
        let battery_msgs = {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("Unable to get current time");
            let time = builtin_interfaces::Time {
                sec: now.as_secs() as i32,
                nanosec: now.subsec_nanos(),
            };
            BatteryStatus {
                stamp: time.clone(),
                energy_level: battery,
            }
        };
        let serialized_battery = cdr::serialize::<_, _, CdrLe>(&battery_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
        battery_pub
            .put(serialized_battery)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let mut hazard_pub = self.hazard_publisher.lock().unwrap();
        let hazard_msgs = {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("Unable to get current time");
            let time = builtin_interfaces::Time {
                sec: now.as_secs() as i32,
                nanosec: now.subsec_nanos(),
            };
            autoware_vehicle_msgs::HazardLightsReport {
                stamp: time.clone(),
                report: hazard,
            }
        };
        let serialized_hazard = cdr::serialize::<_, _, CdrLe>(&hazard_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
        hazard_pub
            .put(serialized_hazard)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let mut turn_signal_pub = self.turn_signal_publisher.lock().unwrap();
        let turn_signal_msgs = {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("Unable to get current time");
            let time = builtin_interfaces::Time {
                sec: now.as_secs() as i32,
                nanosec: now.subsec_nanos(),
            };
            autoware_vehicle_msgs::TurnIndicatorsReport {
                stamp: time.clone(),
                report: turn_signal,
            }
        };
        let serialized_turn_signal = cdr::serialize::<_, _, CdrLe>(&turn_signal_msgs, Infinite)
            .map_err(|err| pyo3::exceptions::PyException::new_err(err.to_string()))?;
        turn_signal_pub
            .put(serialized_turn_signal)
            .wait()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    
        Ok(())
    }
}

#[pymodule]
fn beamng_publisher(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BeamngPublisher>()?;
    Ok(())
}
