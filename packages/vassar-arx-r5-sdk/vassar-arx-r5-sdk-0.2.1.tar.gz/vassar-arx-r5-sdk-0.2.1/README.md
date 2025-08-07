# ARX R5 SDK for Python

Python SDK for controlling ARX R5 robot arms via CAN interface on Linux systems.

## System Requirements

- **Operating System**: Ubuntu 22.04 LTS or Ubuntu 24.04 LTS
- **Python**: 3.10, 3.11, or 3.12
- **Hardware**: ARX R5 robot arm with CAN interface
- **Architecture**: x86_64 or ARM64/aarch64

## Prerequisites

### 1. CAN Interface Setup

Install CAN utilities:
```bash
sudo apt update
sudo apt install can-utils net-tools
```

### 2. Build Dependencies (if building from source)

```bash
# Install CMake and build tools
sudo apt install cmake build-essential

# Install pybind11
pip install pybind11
```

## Installation

### Install from PyPI (Recommended)

Pre-built wheels are available for Ubuntu 22.04 and 24.04 LTS:

```bash
pip install vassar-arx-r5-sdk
```

### Install from Source

```bash
git clone https://github.com/yourusername/arx-r5-sdk.git
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

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Robot arm falls or unresponsive | Check for "safe mode" message, power cycle if needed |
| CAN port won't open | Check connections, replug USB, re-enable CAN interface |
| Motor connection failed | Reconnect base connector |
| Program stuck at initialization | Ensure sufficient USB bandwidth, avoid sharing with WiFi dongles |

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