#!/usr/bin/env python3
"""
Rapid Relay Controller for Sequent Microsystems 8RELIND Board
===========================================================
Simply press keys 1-8 to activate the corresponding relay.
The relay will rapidly toggle on/off for 5 seconds.

Usage:
    python3 rapid_relay_script.py
"""

import os
import time
import sys

# Configuration
BOARD_ID = 7
RAPID_TOGGLE_DURATION = 5  # seconds to run the rapid toggling
TOGGLE_DELAY = 0.1  # shorter delay for rapid toggling

def run_command(cmd):
    """Run a shell command"""
    print(f"Command: {cmd}")
    os.system(cmd)

def rapid_toggle_relay(relay_num):
    """Rapidly toggle relay ON-OFF for 5 seconds"""
    print(f"\nRapidly toggling relay {relay_num} for {RAPID_TOGGLE_DURATION} seconds...")
    
    # Calculate how many toggles we can fit in the duration
    end_time = time.time() + RAPID_TOGGLE_DURATION
    
    # Keep toggling until we reach the time limit
    toggle_count = 0
    while time.time() < end_time:
        # ON
        run_command(f"8relind {BOARD_ID} write {relay_num} on")
        time.sleep(TOGGLE_DELAY)
        
        # OFF
        run_command(f"8relind {BOARD_ID} write {relay_num} off")
        time.sleep(TOGGLE_DELAY)
        
        toggle_count += 1
    
    print(f"Completed {toggle_count} toggles for relay {relay_num}")

# Print instructions
print("=== Rapid Relay Controller ===")
print("Press keys 1-8 to activate relays")
print("Each relay will rapidly toggle on/off for 5 seconds")
print("Press Ctrl+C to exit")
print("=============================")

# Main loop
try:
    while True:
        # Simple input
        key = input("Enter relay (1-8): ")
        
        # Check for valid relay number
        if key in ['1', '2', '3', '4', '5', '6', '7', '8']:
            rapid_toggle_relay(int(key))
        elif key.lower() in ['q', 'quit', 'exit']:
            break
        else:
            print("Please enter a number between 1 and 8")
except KeyboardInterrupt:
    print("\nExiting...")

# Turn off all relays on exit
print("Turning all relays off...")
for i in range(1, 9):
    run_command(f"8relind {BOARD_ID} write {i} off")

print("Goodbye!")