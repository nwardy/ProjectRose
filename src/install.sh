#!/bin/bash
# Installation script for 8-Relay Sequencer

# Display banner
echo "================================================"
echo "    8-Relay Sequencer Installation Script     "
echo "    For Sequent Microsystems 8RELIND Board    "
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo && ! grep -q "raspberrypi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi."
    echo "The script will continue, but may not work correctly on this system."
    echo ""
fi

# Create directory for the application
echo "Creating application directory..."
mkdir -p ~/relay-sequencer
cd ~/relay-sequencer

# Check if Sequent Microsystems library is installed
echo "Checking for Sequent Microsystems 8RELIND library..."
if [ ! -d "/usr/local/bin/8relind" ] && ! pip3 list | grep -q "lib8relind"; then
    echo "8RELIND library not found. Installing..."
    
    # Install dependencies
    echo "Installing dependencies..."
    sudo apt-get update
    sudo apt-get install -y git build-essential python3-pip python3-dev python3-smbus

    # Clone and install the Sequent Microsystems repository
    echo "Cloning 8RELIND repository..."
    git clone https://github.com/SequentMicrosystems/8relind-rpi.git
    cd 8relind-rpi
    
    echo "Installing command line tool..."
    sudo make install
    
    echo "Installing Python library..."
    cd python
    sudo pip3 install .
    
    cd ~/relay-sequencer
else
    echo "8RELIND library already installed."
fi

# Also create simple command-line version
echo "Creating simple command-line version..."
cat > ~/relay-sequencer/simple_relay_control.py << 'EOL'
#!/usr/bin/env python3
"""
Simple Relay Control Script for Sequent Microsystems 8RELIND Board
==================================================================
This simplified script demonstrates how to cycle through each relay on the board,
turning each one on and off in a pattern before moving to the next relay.
It's designed to be as simple as possible for testing purposes.

Usage:
    python simple_relay_control.py [stack_level]

    stack_level: Optional parameter for the stack level of the card (0-7)
                 Default is 0 if not specified

Controls:
    CTRL+C - Exit the application
"""

import sys
import time

# Check if running on Raspberry Pi with the lib8relind module
try:
    import lib8relind
    SIMULATION_MODE = False
except ImportError:
    print("Warning: lib8relind not found, running in simulation mode")
    print("This script will run in simulation mode for testing on non-Raspberry Pi systems.")
    SIMULATION_MODE = True

# Constants
RELAY_COUNT = 8
DEFAULT_STACK = 0
TOGGLE_COUNT = 3       # Number of times to toggle each relay
TOGGLE_DELAY = 0.5     # Delay between on/off in seconds
SEQUENCE_DELAY = 1.0   # Delay before moving to next relay

class RelayBoard:
    """Simple interface to the 8RELIND relay board"""
    
    def __init__(self, stack=DEFAULT_STACK):
        self.stack = stack
        self.simulation = SIMULATION_MODE
        self.relay_states = [0] * RELAY_COUNT
        
        # Initialize the board - turn all relays off
        self.set_all(0)
    
    def set_relay(self, relay_num, state):
        """Set state of a single relay (1-8)"""
        if relay_num < 1 or relay_num > RELAY_COUNT:
            return False
        
        if self.simulation:
            self.relay_states[relay_num-1] = state
            print(f"Relay {relay_num}: {'ON' if state else 'OFF'}")
            return True
        
        try:
            lib8relind.set(self.stack, relay_num, state)
            return True
        except Exception as e:
            print(f"Error setting relay {relay_num}: {e}")
            return False
    
    def get_relay(self, relay_num):
        """Get state of a single relay (1-8)"""
        if relay_num < 1 or relay_num > RELAY_COUNT:
            return 0
        
        if self.simulation:
            return self.relay_states[relay_num-1]
        
        try:
            return lib8relind.get(self.stack, relay_num)
        except Exception as e:
            print(f"Error getting relay {relay_num}: {e}")
            return 0
    
    def set_all(self, value):
        """Set all relays based on bitmap value (0-255)"""
        if self.simulation:
            for i in range(RELAY_COUNT):
                self.relay_states[i] = 1 if (value & (1 << i)) else 0
            if value > 0:
                print(f"All relays set to: {bin(value)[2:].zfill(8)}")
            else:
                print("All relays OFF")
            return True
        
        try:
            lib8relind.set_all(self.stack, value)
            return True
        except Exception as e:
            print(f"Error setting all relays: {e}")
            return False
            
    def toggle_relay_pattern(self, relay_num):
        """Toggle a relay on and off in the specified pattern"""
        print(f"\n--- Toggling Relay {relay_num} ---")
        
        # Initial on state
        self.set_relay(relay_num, 1)
        time.sleep(TOGGLE_DELAY)
        
        # Toggle the specified number of times
        for i in range(TOGGLE_COUNT):
            # Off
            self.set_relay(relay_num, 0)
            time.sleep(TOGGLE_DELAY)
            
            # On
            self.set_relay(relay_num, 1)
            time.sleep(TOGGLE_DELAY)
        
        # Final state: off
        self.set_relay(relay_num, 0)
        time.sleep(SEQUENCE_DELAY)  # Pause before next relay


    def run_sequence(self):
        """Run through all relays in sequence"""
        print(f"Starting relay sequence on stack {self.stack}")
        print("Press CTRL+C to exit")
        print("----------------------------")
        
        try:
            while True:  # Run continuously until interrupted
                # Cycle through all relays
                for relay in range(1, RELAY_COUNT + 1):
                    self.toggle_relay_pattern(relay)
                    
        except KeyboardInterrupt:
            # Clean up on CTRL+C
            print("\nSequence interrupted by user")
            self.set_all(0)  # Turn all relays off
            print("All relays turned OFF")


def main():
    """Main entry point"""
    # Get stack level from command line argument
    stack = DEFAULT_STACK
    if len(sys.argv) > 1:
        try:
            stack = int(sys.argv[1])
            if stack < 0 or stack > 7:
                print("Error: Stack level must be between 0 and 7")
                sys.exit(1)
        except ValueError:
            print("Error: Invalid stack level provided")
            sys.exit(1)
    
    # Create and run board
    board = RelayBoard(stack)
    board.run_sequence()


if __name__ == "__main__":
    main()
EOL

chmod +x ~/relay-sequencer/simple_relay_control.py

# Create hardware test script
echo "Creating hardware test script..."
cat > ~/relay-sequencer/relay_test.sh << 'EOL'
#!/bin/bash
# Test script for the 8-Relay board
# This script quickly cycles through all relays for a quick hardware test

echo "====================================================="
echo "     8-RELAY HARDWARE TEST SCRIPT                    "
echo "     For Sequent Microsystems 8RELIND Board          "
echo "====================================================="
echo

# Check if the 8relind command is available
if ! command -v 8relind &> /dev/null; then
    echo "Error: 8relind command not found."
    echo "Please make sure the Sequent Microsystems software is installed."
    echo "Run the following commands to install:"
    echo "  git clone https://github.com/SequentMicrosystems/8relind-rpi.git"
    echo "  cd 8relind-rpi"
    echo "  sudo make install"
    exit 1
fi

# Ensure all relays are off at the start
echo "Turning all relays OFF..."
8relind writeall 0 0

echo "Starting relay test sequence..."
echo "CTRL+C to exit"
echo

# Function to toggle a relay
toggle_relay() {
    local relay=$1
    local stack=${2:-0}
    
    echo -n "Testing relay $relay: "
    
    # Turn on
    echo -n "ON > "
    8relind write $stack $relay 1
    sleep 0.3
    
    # Turn off
    echo "OFF"
    8relind write $stack $relay 0
    sleep 0.2
}

# Function to run a full test cycle
test_cycle() {
    local stack=${1:-0}
    
    echo "--- Testing stack $stack ---"
    
    # Test each relay in sequence
    for relay in {1..8}; do
        toggle_relay $relay $stack
    done
    
    echo "--- All relays tested ---"
    echo
}

# Run the test continuously until CTRL+C is pressed
trap 'echo -e "\nTest interrupted. Turning all relays OFF..."; 8relind writeall 0 0; echo "Done."; exit 0' INT

while true; do
    # Run the test on stack 0 (default stack)
    # Change this if testing a different stack
    test_cycle 0
    
    # Brief pause between cycles
    sleep 1
done
EOL

chmod +x ~/relay-sequencer/relay_test.sh

# Copy the relay sequencer application
echo "Installing relay sequencer application..."

# Create the main application file
cat > ~/relay-sequencer/relay_sequencer.py << 'EOL'
#!/usr/bin/env python3
"""
8-Relay Sequencer for Sequent Microsystems 8RELIND Raspberry Pi HAT
====================================================================
This application cycles through each relay on the board, turning each one
on and off in a pattern before moving to the next relay.

Usage:
    python relay_sequencer.py [stack_level]

    stack_level: Optional parameter for the stack level of the card (0-7)
                 Default is 0 if not specified

Controls:
    ENTER      - Start/pause the sequence
    SPACE      - Skip to next relay
    1-8        - Toggle specific relay (1-8)
    ESC or Q   - Exit the application
"""

import sys
import time
import curses
import threading
from curses import wrapper

# Check if running on Raspberry Pi with the lib8relind module
try:
    import lib8relind
    SIMULATION_MODE = False
except ImportError:
    print("Warning: lib8relind not found, running in simulation mode")
    SIMULATION_MODE = True

# Constants
RELAY_COUNT = 8
DEFAULT_STACK = 0
TOGGLE_COUNT = 3       # Number of times to toggle each relay
TOGGLE_DELAY = 0.5     # Delay between on/off in seconds
SEQUENCE_DELAY = 1.0   # Delay before moving to next relay

class RelayBoard:
    """Interface to the 8RELIND relay board"""
    
    def __init__(self, stack=DEFAULT_STACK):
        self.stack = stack
        self.simulation = SIMULATION_MODE
        self.relay_states = [0] * RELAY_COUNT
        
        # Initialize the board - turn all relays off
        self.set_all(0)
    
    def set_relay(self, relay_num, state):
        """Set state of a single relay (1-8)"""
        if relay_num < 1 or relay_num > RELAY_COUNT:
            return False
        
        if self.simulation:
            self.relay_states[relay_num-1] = state
            return True
        
        try:
            lib8relind.set(self.stack, relay_num, state)
            return True
        except Exception as e:
            print(f"Error setting relay {relay_num}: {e}")
            return False
    
    def get_relay(self, relay_num):
        """Get state of a single relay (1-8)"""
        if relay_num < 1 or relay_num > RELAY_COUNT:
            return 0
        
        if self.simulation:
            return self.relay_states[relay_num-1]
        
        try:
            return lib8relind.get(self.stack, relay_num)
        except Exception as e:
            print(f"Error getting relay {relay_num}: {e}")
            return 0
    
    def set_all(self, value):
        """Set all relays based on bitmap value (0-255)"""
        if self.simulation:
            for i in range(RELAY_COUNT):
                self.relay_states[i] = 1 if (value & (1 << i)) else 0
            return True
        
        try:
            lib8relind.set_all(self.stack, value)
            return True
        except Exception as e:
            print(f"Error setting all relays: {e}")
            return False
    
    def get_all(self):
        """Get states of all relays as a bitmap (0-255)"""
        if self.simulation:
            value = 0
            for i in range(RELAY_COUNT):
                if self.relay_states[i]:
                    value |= (1 << i)
            return value
        
        try:
            return lib8relind.get_all(self.stack)
        except Exception as e:
            print(f"Error getting all relays: {e}")
            return 0

class RelaySequencer:
    """Main application for sequencing relay patterns"""
    
    def __init__(self, stdscr, stack=DEFAULT_STACK):
        self.stdscr = stdscr
        self.board = RelayBoard(stack)
        self.current_relay = 1
        self.running = False
        self.exiting = False
        self.sequence_thread = None
        
        # Initialize curses
        self.init_curses()
    
    def init_curses(self):
        """Setup curses environment"""
        curses.curs_set(0)  # Hide cursor
        curses.use_default_colors()
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_GREEN, -1)  # On state
            curses.init_pair(2, curses.COLOR_RED, -1)    # Off state
            curses.init_pair(3, curses.COLOR_YELLOW, -1) # Highlight
        
        self.stdscr.timeout(100)  # Non-blocking input with 100ms timeout
        self.stdscr.clear()
    
    def draw_ui(self):
        """Draw the user interface"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # Title
        title = "8-Relay Sequencer"
        self.stdscr.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Status line
        status = f"Stack: {self.board.stack} | "
        status += "RUNNING" if self.running else "PAUSED"
        if self.board.simulation:
            status += " | SIMULATION MODE"
        self.stdscr.addstr(3, 2, status)
        
        # Draw relay states
        self.stdscr.addstr(5, 2, "Relay Status:")
        for i in range(RELAY_COUNT):
            relay_num = i + 1
            state = self.board.get_relay(relay_num)
            
            # Highlight current relay
            attr = curses.A_NORMAL
            if relay_num == self.current_relay:
                attr |= curses.A_BOLD
                if curses.has_colors():
                    attr |= curses.color_pair(3)
            
            # Color state
            state_str = "ON " if state else "OFF"
            state_attr = attr
            if curses.has_colors():
                if state:
                    state_attr |= curses.color_pair(1)
                else:
                    state_attr |= curses.color_pair(2)
            
            self.stdscr.addstr(6 + i, 4, f"Relay {relay_num}: ", attr)
            self.stdscr.addstr(state_str, state_attr)
        
        # Help
        help_text = [
            "Controls:",
            "ENTER      - Start/pause sequence",
            "SPACE      - Skip to next relay",
            "1-8        - Toggle specific relay",
            "ESC or Q   - Exit"
        ]
        
        for i, line in enumerate(help_text):
            self.stdscr.addstr(6 + i, width - len(line) - 4, line)
        
        self.stdscr.refresh()
    
    def toggle_relay_sequence(self, relay_num):
        """Toggle a relay on and off multiple times"""
        # Initial toggle on
        self.board.set_relay(relay_num, 1)
        self.draw_ui()
        time.sleep(TOGGLE_DELAY)
        
        # Toggle TOGGLE_COUNT times
        for i in range(TOGGLE_COUNT):
            # Off
            self.board.set_relay(relay_num, 0)
            self.draw_ui()
            if self.exiting or not self.running:
                break
            time.sleep(TOGGLE_DELAY)
            
            # On
            self.board.set_relay(relay_num, 1)
            self.draw_ui()
            if self.exiting or not self.running:
                break
            time.sleep(TOGGLE_DELAY)
        
        # Final state: off
        self.board.set_relay(relay_num, 0)
        self.draw_ui()
        
        # Pause before next relay
        if not self.exiting and self.running:
            time.sleep(SEQUENCE_DELAY)
    
    def sequence_worker(self):
        """Background thread to handle the relay sequence"""
        while not self.exiting and self.running:
            # Perform sequence on current relay
            self.toggle_relay_sequence(self.current_relay)
            
            # Move to next relay if not paused
            if not self.exiting and self.running:
                self.current_relay = (self.current_relay % RELAY_COUNT) + 1
        
        # Reset sequence thread when stopped
        if not self.exiting:
            self.sequence_thread = None
    
    def start_sequence(self):
        """Start the relay sequence"""
        if not self.running and not self.sequence_thread:
            self.running = True
            self.sequence_thread = threading.Thread(target=self.sequence_worker)
            self.sequence_thread.daemon = True
            self.sequence_thread.start()
    
    def stop_sequence(self):
        """Stop the relay sequence"""
        self.running = False
    
    def next_relay(self):
        """Skip to the next relay"""
        if not self.running:
            self.current_relay = (self.current_relay % RELAY_COUNT) + 1
            self.draw_ui()
    
    def toggle_relay(self, relay_num):
        """Manually toggle a specific relay"""
        if 1 <= relay_num <= RELAY_COUNT:
            state = self.board.get_relay(relay_num)
            self.board.set_relay(relay_num, 1 - state)  # Toggle state
            self.draw_ui()
    
    def handle_input(self, key):
        """Process user input"""
        if key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter key
            if self.running:
                self.stop_sequence()
            else:
                self.start_sequence()
        
        elif key == 32:  # Space key
            self.next_relay()
        
        elif 49 <= key <= 56:  # 1-8 keys
            relay_num = key - 48  # Convert ASCII to number
            self.toggle_relay(relay_num)
        
        elif key == 27 or key == 113 or key == 81:  # Esc or Q/q
            self.exiting = True
            self.stop_sequence()
            return False  # Signal to exit main loop
        
        return True  # Continue main loop
    
    def cleanup(self):
        """Clean up resources before exit"""
        # Turn all relays off
        self.board.set_all(0)
        
        # Wait for sequence thread to finish if running
        if self.sequence_thread:
            self.sequence_thread.join(1.0)  # Wait up to 1 second
    
    def run(self):
        """Main application loop"""
        try:
            while not self.exiting:
                # Draw UI
                self.draw_ui()
                
                # Get input
                key = self.stdscr.getch()
                if key != -1:  # -1 is returned on timeout
                    if not self.handle_input(key):
                        break
                
                # Small delay to prevent CPU hogging
                time.sleep(0.01)
        finally:
            self.cleanup()

def main(stdscr):
    """Main entry point for curses application"""
    # Get stack level from command line argument
    stack = DEFAULT_STACK
    if len(sys.argv) > 1:
        try:
            stack = int(sys.argv[1])
            if stack < 0 or stack > 7:
                raise ValueError("Stack level must be between 0 and 7")
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    # Create and run the sequencer
    sequencer = RelaySequencer(stdscr, stack)
    sequencer.run()
    return 0

if __name__ == "__main__":
    try:
        exit_code = wrapper(main)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(0)