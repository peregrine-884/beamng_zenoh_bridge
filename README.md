# zenoh_beamng_bridge
This repository provides a bridge between BeamNG and ROS 2 using Zenoh, enabling real-time data transfer from BeamNG to ROS 2 topics. This integration allows users to simulate driving scenarios in BeamNG and utilize the data within the ROS 2 ecosystem for further processing, visualization, or autonomous driving applications.

# Getting Started
## 1. Set up a Rust development environment on Windows
### Install Rust
download and run [rustup-init.exe](https://win.rustup.rs/)  

### Verify Rust Installation
To ensure that Rust is installed correctly, you can use the following commands:  

**1. Check the Rust version:**  
```bash
rustc --version
```
**2. Check the Cargo version:**
```bash
cargo --version
```

If both commands return the version information, Rust is successfully installed on your system

###  Install Rust Nightly and Required Python Packages for PyO3
**1. Install Rust Nightyly**  

To use PyO3, you need to install the nightly version of Rust.Run the following command:
```bash
rustup install nightly
rustup default nightly
```

## 2. Install beamngpy
To utilize the BeamNG API, run the following command:
```bash
pip install beamngpy==1.30
```

## 3. Install eclipse-zenoh
To enable data communication with Zenoh, install the `eclipse-zenoh` library
```bash
pip install eclipse-zenoh==1.0.0a6
```

## 4. Install Python Packages
Next, install the required Python packages
```bash
pip install setuptools
pip install setuptools-rust
pip install pycdr2
pip install keyboard
```

## 5. Clone and build the project
To use this project, first clone the repository and build it. This will prepare the Rust functions for use in Python. Follow these steps:

```
# clone the repository
cd ~/
git clone https://github.com/hayato-hayashi/zenoh_beamng_bridge.git

# move into the cloned directory
cd ~/zenoh_beamng_bridge/beamng_publisher

# build
python setup.py install
```

# Usage
To run the application, you will need to use two terminal windows

### Terminal 1
```bash
# Move to the directory where BeamNG.tech is located
cd <path-to-beamng.tech-directory>

# Run the BeamNG.tech application
Bin64\BeamNG.tech.x64.exe -console -nosteam -tcom-listen-ip "127.0.0.1" -lua "extensions.load('tech/techCore');tech_techCore.openServer(64256)"
```

### Terminal 2
```bash
cd ~/zenoh_beamng_bridge/beamng
python main.py
```





