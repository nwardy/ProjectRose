# ProjectRose 8-Relay Sequencer

Control application for Sequent Microsystems 8RELIND board on Raspberry Pi.

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/nwardy/ProjectRose.git
   cd ProjectRose
   ```

2. Run the installation script:
   ```bash
   chmod +x src/install_script.sh
   ./src/install_script.sh
   ```

3. Start the relay control:
   ```bash
   cd ~/relay-sequencer
   ./run_simple.sh
   ```

## What It Does

Automatically cycles through each of the 8 relays on the Sequent Microsystems board, toggling them on and off multiple times before moving to the next relay. Press CTRL+C to exit.

## Hardware Requirements

- Raspberry Pi (any model)
- Sequent Microsystems 8RELIND board
- Bluetooth USB keyboard for control

## File Structure

```
src/
├── install_script.sh      # Installation script
├── simple_relay_control.py # Main control script
└── requirements.txt       # Python dependencies
```