#!/usr/bin/env python3
"""
Basic Relay Controller for Sequent Microsystems 8RELIND Board
============================================================
Simple controller that uses the native 8relind command.

Usage:
    python3 basic_relay_control.py

Enter relay numbers 1-8 to activate the pattern.
"""

import subprocess
import time
import sys
import threading

# Constants
BOARD_ID = 7
TOGGLE_DELAY = 0.75
relay_busy = [False] * 8

def run_command(cmd):
    """Run a shell command and return the result"""
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.SubprocessError:
        print(f"Error running command: {cmd}")
        return False

def toggle_relay(relay_num):
    """Toggle a relay in the ON-OFF-ON-OFF pattern"""
    relay_idx = relay_num - 1
    
    # Skip if relay is already in use
    if relay_busy[relay_idx]:
        print(f"Relay {relay_num} is already busy")
        return
    
    relay_busy[relay_idx] = True
    
    try:
        print(f"Activating relay {relay_num} pattern...")
        
        # ON
        run_command(f"8relind write {BOARD_ID} {relay_num} 1")
        time.sleep(TOGGLE_DELAY)
        
        # OFF
        run_command(f"8relind write {BOARD_ID} {relay_num} 0")
        time.sleep(TOGGLE_DELAY)
        
        # ON
        run_command(f"8relind write {BOARD_ID} {relay_num} 1")
        time.sleep(TOGGLE_DELAY)
        
        # OFF (final state)
        run_command(f"8relind write {BOARD_ID} {relay_num} 0")
        
        print(f"Relay {relay_num} pattern complete")
    finally:
        relay_busy[relay_idx] = False

# Main program
print("=== Basic Relay Controller ===")
print(f"Board ID: {BOARD_ID}")
print("Enter a relay number (1-8) to toggle it")
print("Type 'q' to quit")
print("==============================")

# Turn all relays off at start
print("Turning all relays off...")
for i in range(1, 9):
    run_command(f"8relind write {BOARD_ID} {i} 0")

# Main loop
running = True
while running:
    try:
        user_input = input("> ")
        
        # Check for quit command
        if user_input.lower() in ('q', 'quit', 'exit'):
            running = False
            continue
        
        # Check for valid relay number
        if user_input.isdigit():
            relay_num = int(user_input)
            if 1 <= relay_num <= 8:
                # Create a thread to handle the relay pattern
                thread = threading.Thread(target=toggle_relay, args=(relay_num,))
                thread.daemon = True
                thread.start()
            else:
                print("Please enter a number between 1 and 8")
    except KeyboardInterrupt:
        running = False
    except Exception as e:
        print(f"Error: {e}")

# Turn all relays off when exiting
print("\nExiting... Turning all relays off")
for i in range(1, 9):
    run_command(f"8relind write {BOARD_ID} {i} 0")

print("Goodbye!")