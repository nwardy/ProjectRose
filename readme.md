# ProjectRose - Relay Controller

Simple controller for Sequent Microsystems 8RELIND board on Raspberry Pi.

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/nwardy/ProjectRose.git
   cd ProjectRose
   ```

2. Install required Python package:
   ```bash
   pip3 install readchar
   ```

3. Run the installation script:
   ```bash
   chmod +x src/install.sh
   ./src/install.sh
   ```

4. Start the relay controller:
   ```bash
   cd ~/relay-controller
   ./start.sh
   ```

## How It Works

- Press any key from 1-8 to activate the corresponding relay
- The relay will toggle in a pattern: ON-OFF-ON-OFF (with 0.75 second delays)
- Press Q or Ctrl+C to exit

## Command Line Options

You can specify the board ID (0-7) when starting:
```bash
./start.sh 2  # Use board with ID 2
```
Default board ID is 7 if not specified.

## Hardware Requirements

- Raspberry Pi (any model)
- Sequent Microsystems 8RELIND board
- Keyboard for input

## File Structure

```
src/
├── install.sh             # Installation script
└── simple_relay_control.py # Main control script
```