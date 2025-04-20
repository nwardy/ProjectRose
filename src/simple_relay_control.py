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