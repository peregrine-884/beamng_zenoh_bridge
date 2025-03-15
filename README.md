# zenoh_beamng_bridge
## 1. BeamNG  
BeamNG is software equipped with a physics engine that enables realistic vehicle simulations. Notably, it can simulate realistic collisions and vehicle behavior, making it widely used for applications ranging from gaming to research and development.

BeamNG has two main versions:

- **BeamNG.drive**: A consumer driving simulator for free driving and vehicle physics.
- **BeamNG.tech**: A research and development version.

To access sensor data (e.g., cameras, LiDAR, vehicle states) and interact with the simulation programmatically, **BeamNG.tech is required**.
This version (0.32) is typically run on **Windows** to ensure proper functionality.

A valid license is required to use BeamNG.tech.

For licensing details, please visit the official [BeamNG.tech website](https://www.beamng.tech) and scroll down to the **Licensing Inquiry** section at the bottom of the page.

## 2. Zenoh
Zenoh is a high-performance, distributed data platform designed for real-time data exchange in IoT, robotics, and distributed systems. It offers low-latency communication, efficient data transfer, and seamless integration across edge devices, cloud systems, and hybrid environments.

### Key Features:
- **Low-latency Communication**: Essential for real-time applications like autonomous driving.
- **Data-Centric**: Flexible data publication and subscription across networks.
- **Scalable**: Works on both embedded systems and cloud infrastructures.
- **Interoperability**: Supports various transport protocols for system integration.

### Supported Languages:
- **C/C++**, **Rust**, **Python**, and **Go** are supported, allowing integration into a wide range of systems and applications.

## 3. Installation and Setup
Follow these steps to set up the development environment for the project.

### Set up a Virtual Environment
1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
venv\Scripts\activate
```

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Set up the Rust Environment
Since Zenoh is written in Rust, you'll need to set up a Rust development environment.

1. Install Rust by downloading and running the installer from [rustup-init.exe](https://win.rustup.rs/).

2. Verify the installation of Rust:
```bash
rustc --version
cargo --version
```

### Enable Rust Functions in Python
After setting up the Rust environment, you can integrate Rust functions with Python using PyO3 and build the Rust project.

1. Install the nightly version of Rust, which is required for PyO3 (used for integrating Rust with Python):
```bash
rustup install nightly
rustup default nightly
```

2. Install the necessary Python packages for Rust integration:
```bash
pip install setuptools
pip install setuptools-rust
```

3. Build the Rust functions for Python:
```bash
cd this-repository\zenoh_bridge
python setup.py install
```

## What You Can Do with This Repository

This repository enables vehicle control using **Autoware** in conjunction with **BeamNG.tech**, allowing for autonomous driving simulations and map generation.

### Running BeamNG.tech
1. Open a terminal and navigate to the directory where **BeamNG.tech** is located:
   ```bash
   cd <path-to-beamng.tech-directory>
   ```

2. Run the **BeamNG.tech** application with the following command:
   ```bash
   Bin64\BeamNG.tech.x64.exe -console -nosteam -tcom-listen-ip "127.0.0.1" -lua "extensions.load('tech/techCore');tech_techCore.openServer(64256)"
   ```
   This will start **BeamNG.tech** and make it ready to communicate with other systems (e.g., Autoware) via TCP/IP.

### Running Scripts
1. Open a second terminal and navigate to the `scripts` directory of this repository:
   ```bash
   cd this-repository\scripts
   ```

2. Run the script that suits your needs:

- **autoware_drive.bat**: Activates autonomous driving using **Autoware** and **BeamNG.tech**.
- **create_accel_brake_map.bat**: Generates an **accel-brake map** for controlling vehicle acceleration and braking.
- **create_pointcloud_map.bat**: Creates a point cloud map (.pcd) for mapping and localization in **Autoware**.
