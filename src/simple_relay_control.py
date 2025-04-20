#!/usr/bin/env python3
"""
Simple Relay Controller for Sequent Microsystems 8RELIND Board
===========================================================
Simply press keys 1-8 to activate the corresponding relay.

Usage:
    python3 simple_relay_script.py
"""

import os
import time
import sys

# Configuration
BOARD_ID = 7
TOGGLE_DELAY = 0.75

def run_command(cmd):
    """Run a shell command"""
    print(f"Command: {cmd}")
    os.system(cmd)

def toggle_relay(relay_num):
    """Toggle relay in ON-OFF-ON-OFF pattern"""
    print(f"\nActivating relay {relay_num}")
    
    # ON
    run_command(f"8relind {BOARD_ID} write {relay_num} on")
    time.sleep(TOGGLE_DELAY)
    
    # OFF
    run_command(f"8relind {BOARD_ID} write {relay_num} off")
    time.sleep(TOGGLE_DELAY)
    
    # ON
    run_command(f"8relind {BOARD_ID} write {relay_num} on")
    time.sleep(TOGGLE_DELAY)
    
    # OFF
    run_command(f"8relind {BOARD_ID} write {relay_num} off")
    
    print(f"Relay {relay_num} pattern complete")

# Print instructions
print("=== Simple Relay Controller ===")
print("Press keys 1-8 to activate relays")
print("Press Ctrl+C to exit")
print("=============================")

# Main loop
try:
    while True:
        # Simple input without using readchar
        key = input("Enter relay (1-8): ")
        
        # Check for valid relay number
        if key in ['1', '2', '3', '4', '5', '6', '7', '8']:
            toggle_relay(int(key))
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