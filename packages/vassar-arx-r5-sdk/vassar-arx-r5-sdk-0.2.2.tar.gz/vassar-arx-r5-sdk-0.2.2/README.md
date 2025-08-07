# ARX R5 SDK for Python

Python SDK for controlling ARX R5 robot arms via CAN interface on Linux systems.

## System Requirements

- **Operating System**: Ubuntu 22.04 LTS or Ubuntu 24.04 LTS
- **Python**: 3.10, 3.11, or 3.12
- **Hardware**: ARX R5 robot arm with CAN interface
- **Architecture**: x86_64 or ARM64/aarch64

## Prerequisites

### 1. System Dependencies

All users must install these system dependencies before installing the package:

```bash
# Update package list
sudo apt update

# Install CAN utilities (required for robot communication)
sudo apt install can-utils net-tools

# Install build tools (required for pip installation)
sudo apt install cmake build-essential
```

### 2. Install pybind11 globally

The package requires pybind11 to be installed globally via CMake:

```bash
# Clone and install pybind11
git clone https://github.com/pybind/pybind11.git
cd pybind11
mkdir build && cd build
cmake .. -DPYBIND11_TEST=OFF
make -j4
sudo make install
cd ../..
rm -rf pybind11  # Clean up
```

## Installation

### Install from PyPI

**Note**: This package is distributed as source only. The installation will compile C++ extensions on your system.

```bash
# Install Python dependencies
pip install numpy

# Install the package (this will compile during installation)
pip install vassar-arx-r5-sdk
```

The installation process will:
- Download the source package
- Compile the C++ Python bindings
- Install the package with pre-built ARM libraries

### Install from Source

```bash
git clone https://github.com/vassar-robotics/arx-r5-sdk.git
cd arx-r5-sdk
pip install .
```

## Usage

### Basic Example - Single Arm Control

```python
from vassar_arx_r5_sdk.bimanual import SingleArm
import numpy as np

# Configure the robot arm
arm_config = {
    "can_port": "can0",  # or "can1" depending on your setup
    "type": 0,           # 0 for X5liteaa0, other values for R5_master
    "num_joints": 7,     # Number of joints (default: 7)
    "dt": 0.05          # Control time step in seconds (default: 0.05)
}

# Initialize the arm
arm = SingleArm(arm_config)

# Move to home position
arm.go_home()

# Control via joint positions
positions = [0.0, 0.5, -0.5, 0.0, 0.0, 0.0]  # 6 joint angles
arm.set_joint_positions(positions)

# Control via end-effector pose
position = np.array([0.3, 0.0, 0.2])  # x, y, z in meters
quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # w, x, y, z
arm.set_ee_pose(pos=position, quat=quaternion)

# Get current state
joint_positions = arm.get_joint_positions()
joint_velocities = arm.get_joint_velocities()
ee_pose = arm.get_ee_pose()  # Returns [x, y, z, w, x, y, z]

# Enable gravity compensation mode
arm.gravity_compensation()
```

### Dual Arm Control

```python
from vassar_arx_r5_sdk.bimanual import BimanualArm

# Configure both arms
left_arm_config = {
    "can_port": "can0",
    "type": 0
}

right_arm_config = {
    "can_port": "can1",
    "type": 0
}

# Initialize bimanual system
bimanual = BimanualArm(left_arm_config, right_arm_config)

# Move both arms to home
bimanual.go_home()

# Control both arms
positions = {
    "left": [0.0, 0.5, -0.5, 0.0, 0.0, 0.0],
    "right": [0.0, -0.5, 0.5, 0.0, 0.0, 0.0]
}
bimanual.set_joint_positions(positions)
```

### Keyboard Control Example

See the examples directory for a complete keyboard control implementation.

## Important Notes

### Safety

1. **Always use Ctrl+C to stop the program** - Never close the terminal directly
2. Avoid controlling the robot at workspace boundaries to prevent singularities
3. The robot will stop automatically when joint limits are exceeded

### CAN Setup

Before running, ensure your CAN interface is properly configured:
```bash
sudo ip link set can0 up type can bitrate 1000000
```

### Installation Troubleshooting

| Issue | Solution |
|-------|----------|
| CMake not found error | Install with `sudo apt install cmake` |
| pybind11 not found | Follow the pybind11 installation steps in Prerequisites |
| Python.h not found | Install python3-dev package (e.g., `sudo apt install python3.10-dev`) |
| Build fails during pip install | Ensure all prerequisites are installed, check gcc/g++ version |
| Permission denied errors | Use `sudo` for system-wide installation or use virtual environment |

### Runtime Troubleshooting

| Issue | Solution |
|-------|----------|
| Robot arm falls or unresponsive | Check for "safe mode" message, power cycle if needed |
| CAN port won't open | Check connections, replug USB, re-enable CAN interface |
| Motor connection failed | Reconnect base connector |
| Program stuck at initialization | Ensure sufficient USB bandwidth, avoid sharing with WiFi dongles |

## Why Source Distribution Only?

This package is distributed as source code (sdist) rather than pre-built wheels because:

1. **Hardware-specific libraries**: The package includes pre-compiled ARM control libraries (`.so` files) that are specific to the robot hardware
2. **Platform compatibility**: PyPI only accepts manylinux wheels for Linux, not platform-specific wheels (like `linux_x86_64`)
3. **Build customization**: Compiling from source ensures compatibility with your specific system configuration

This means pip will compile the C++ extensions during installation, which is why the build dependencies are required.

## Examples

Complete example scripts are included in the package:
- `test_single_arm.py` - Basic single arm control
- `test_dual_arm.py` - Dual arm coordination
- `test_keyboard.py` - Interactive keyboard control
- `test_kinematic_solver.py` - Kinematic solver usage

## License

This package is distributed under the BSD-3-Clause License. See LICENSE file for details.

## Credits

Original SDK by [ARXrobotics](https://github.com/ARXroboticsX/R5)

Packaged for PyPI by Vassar