#!/usr/bin/env python3
"""
Simple Relay Controller for Sequent Microsystems 8RELIND Board
==============================================================
This script listens for keyboard input (keys 1-8) and controls the corresponding relays.
When a key is pressed, it toggles the relay in a pattern: ON-OFF-ON-OFF

Usage:
    python3 simple_relay_control.py [board_id]

    board_id: Optional parameter for the board ID (0-7)
              Default is 7 if not specified

Controls:
    Keys 1-8      - Activate corresponding relay
    Q or Ctrl+C   - Exit application
"""

import sys
import time
import subprocess
import threading
import readchar
import signal

# Default board id
DEFAULT_BOARD_ID = 7
# Pattern timing in seconds
TOGGLE_DELAY = 0.75
# Flag to control program exit
running = True
# Track which relays are currently running their patterns
relay_busy = [False] * 8

def run_relay_command(board_id, relay_num, state):
    """Run the 8relind command to control a relay"""
    try:
        cmd = f"8relind write {board_id} {relay_num} {1 if state else 0}"
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Error controlling relay {relay_num}: {e}")
        return False

def relay_pattern(board_id, relay_num):
    """Toggle relay in the ON-OFF-ON-OFF pattern"""
    relay_idx = relay_num - 1
    relay_busy[relay_idx] = True

    try:
        print(f"Activating relay {relay_num} pattern...")
        
        # ON
        run_relay_command(board_id, relay_num, True)
        time.sleep(TOGGLE_DELAY)
        
        # OFF
        run_relay_command(board_id, relay_num, False)
        time.sleep(TOGGLE_DELAY)
        
        # ON
        run_relay_command(board_id, relay_num, True)
        time.sleep(TOGGLE_DELAY)
        
        # Final OFF
        run_relay_command(board_id, relay_num, False)
        
        print(f"Relay {relay_num} pattern completed")
    finally:
        relay_busy[relay_idx] = False

def handle_key_press(key, board_id):
    """Handle key press events"""
    global running
    
    # Check for exit keys
    if key in ['q', 'Q', '\x03']:  # q, Q or Ctrl+C
        running = False
        print("Exiting...")
        return
    
    # Check for relay control keys (1-8)
    if key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        relay_num = int(key)
        relay_idx = relay_num - 1
        
        # Only start the pattern if relay is not already busy
        if not relay_busy[relay_idx]:
            # Start relay pattern in a separate thread
            thread = threading.Thread(
                target=relay_pattern,
                args=(board_id, relay_num)
            )
            thread.daemon = True
            thread.start()
        else:
            print(f"Relay {relay_num} is already running")

def signal_handler(sig, frame):
    """Handle interrupt signal (Ctrl+C)"""
    global running
    running = False
    print("\nExiting...")

def main():
    """Main entry point"""
    # Get board ID from command line argument
    board_id = DEFAULT_BOARD_ID
    if len(sys.argv) > 1:
        try:
            board_id = int(sys.argv[1])
            if board_id < 0 or board_id > 7:
                print("Error: Board ID must be between 0 and 7")
                sys.exit(1)
        except ValueError:
            print("Error: Invalid board ID provided")
            sys.exit(1)
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Turn all relays off at start
    print(f"Initializing board {board_id}, turning all relays off...")
    for relay in range(1, 9):
        run_relay_command(board_id, relay, False)
    
    print("\n=== Relay Controller Ready ===")
    print(f"Board ID: {board_id}")
    print("Press keys 1-8 to activate a relay pattern")
    print("Press Q or Ctrl+C to exit")
    print("==============================\n")
    
    # Main input loop
    global running
    while running:
        try:
            # This will block until a key is pressed
            key = readchar.readchar()
            handle_key_press(key, board_id)
        except Exception as e:
            print(f"Error reading key: {e}")
            time.sleep(0.5)  # Avoid tight loop if errors occur
    
    # Make sure all relays are off when exiting
    print("Turning all relays off...")
    for relay in range(1, 9):
        run_relay_command(board_id, relay, False)
    
    print("Goodbye!")

if __name__ == "__main__":
    main()