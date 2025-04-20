# 8-Relay Sequencer for Sequent Microsystems

This repository contains tools for controlling the Sequent Microsystems 8-relay industrial board (8RELIND) for Raspberry Pi. The main application cycles through each relay in sequence, toggling them on and off in a pattern before moving to the next one.

## Features

- **Full UI Sequencer**: A terminal-based interface for controlling relay sequences
- **Simple Command Line Tool**: A simplified version without UI for basic control
- **Hardware Test Script**: A bash script to quickly test all relays
- **Installation Script**: Easy setup of all components

## Requirements

- Raspberry Pi (any model)
- Sequent Microsystems 8RELIND board
- Python 3.x
- Python packages (installed automatically with setup script):
  - python-setuptools
  - wheel
  - smbus
- Internet connection (for initial installation)

## Installation

### Automatic Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/8relind-sequencer.git
   cd 8relind-sequencer
   ```

2. Run the installation script:
   ```bash
   chmod +x setup_script.sh
   ./setup_script.sh
   ```

The script will:
- Check if your system is a Raspberry Pi
- Install required dependencies
- Clone and install the Sequent Microsystems library
- Install all components and create launchers

### Manual Installation

1. Install the Sequent Microsystems library:
   ```bash
   git clone https://github.com/SequentMicrosystems/8relind-rpi.git
   cd 8relind-rpi
   sudo make install
   cd python
   sudo pip3 install .
   ```

2. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Copy the scripts to your preferred location and make them executable:
   ```bash
   chmod +x relay_sequencer.py
   chmod +x simple_relay_control.py
   chmod +x relay_test.sh
   ```

## Usage

### Full UI Sequencer

Run the application:
```bash
cd ~/relay-sequencer
./run.sh [stack_level]
```

Controls:
- **ENTER**: Start/pause the sequence
- **SPACE**: Skip to next relay
- **1-8 keys**: Toggle specific relay (1-8)
- **ESC or Q**: Exit the application

### Simple Command Line Tool

For a simpler interface without curses UI:
```bash
cd ~/relay-sequencer
./run_simple.sh [stack_level]
```

Use CTRL+C to exit.

### Hardware Test Script

For a quick hardware test:
```bash
cd ~/relay-sequencer
./relay_test.sh
```

## Customization

You can customize the behavior by modifying these constants in the code:
- `TOGGLE_COUNT`: Number of times to toggle each relay (default: 3)
- `TOGGLE_DELAY`: Delay between on/off states in seconds (default: 0.5)
- `SEQUENCE_DELAY`: Delay before moving to the next relay (default: 1.0)

## Stack Levels

The Sequent Microsystems 8RELIND board supports stacking multiple boards. You can specify the stack level (0-7) as a command-line parameter to all tools.

The default stack level is 0 if not specified.

## Simulation Mode

If the lib8relind library is not found (e.g., when running on a non-Raspberry Pi system), the application will run in simulation mode, allowing you to test its functionality without actual hardware.

## License

This project is released under the MIT License. See the LICENSE file for details.

## Acknowledgments

- This project uses the [Sequent Microsystems 8RELIND library](https://github.com/SequentMicrosystems/8relind-rpi)