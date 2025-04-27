#!/usr/bin/env python3
"""
Rapid Relay Controller for Sequent Microsystems 8RELIND Board
===========================================================
Simply press keys 1-8 to activate the corresponding relay.
Press * to activate all relays simultaneously.
Press m for a musical easter egg.
Press b for Beauty and the Beast pattern.
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
    """Fire relay once instead of toggling repeatedly"""
    print(f"\nActivating relay {relay_num} once...")
    
    # Turn ON
    run_command(f"8relind {BOARD_ID} write {relay_num} on")
    time.sleep(TOGGLE_DELAY)
    
    # Turn OFF
    run_command(f"8relind {BOARD_ID} write {relay_num} off")
    
    print(f"Relay {relay_num} fired once")

def rapid_toggle_all_relays():
    """Fire all relays once instead of toggling repeatedly"""
    print(f"\nActivating ALL relays once...")
    
    # Turn all relays ON
    for relay in range(1, 9):
        run_command(f"8relind {BOARD_ID} write {relay} on")
    time.sleep(TOGGLE_DELAY)
    
    # Turn all relays OFF
    for relay in range(1, 9):
        run_command(f"8relind {BOARD_ID} write {relay} off")
    
    print(f"All relays fired once")

def play_music_pattern():
    """Play a musical pattern on all relays as an easter egg"""
    print("\n🎵 Playing musical pattern on relays! 🎵")
    
    # Simple musical pattern
    pattern = [
        # Format: ([relays to activate], duration)
        ([1, 3, 5, 7], 0.2),  # Alternating pattern
        ([2, 4, 6, 8], 0.2),  # Alternating pattern
        ([1, 2, 3, 4, 5, 6, 7, 8], 0.3),  # All relays
        ([1, 8], 0.15),  # Outer relays
        ([2, 7], 0.15),  # Moving inward
        ([3, 6], 0.15),  # Moving inward
        ([4, 5], 0.15),  # Inner relays
        ([4, 5], 0.15),  # Inner relays again
        ([3, 6], 0.15),  # Moving outward
        ([2, 7], 0.15),  # Moving outward
        ([1, 8], 0.15),  # Outer relays
        (list(range(1, 9)), 0.1),  # Quick all on
        ([], 0.1),  # All off
        (list(range(1, 9)), 0.1),  # Quick all on
        ([], 0.1),  # All off
        (list(range(1, 9)), 0.3),  # Final all on
        ([], 0.2),  # Final all off
    ]
    
    # Play the pattern
    for relays, duration in pattern:
        # Turn specified relays on
        for relay in relays:
            run_command(f"8relind {BOARD_ID} write {relay} on")
        
        # Wait for the specified duration
        time.sleep(duration)
        
        # Turn all relays off
        for relay in range(1, 9):
            run_command(f"8relind {BOARD_ID} write {relay} off")
        
        # Small pause between notes
        time.sleep(0.05)
    
    print("🎵 Musical pattern complete! 🎵")

def play_beauty_and_beast():
    """Play a Beauty and the Beast inspired pattern on the relays"""
    print("\n🎵 Playing Beauty and the Beast pattern on relays! 🎵")
    
    # Beauty and the Beast inspired pattern
    # Creates a waltz-like pattern with the relays
    pattern = [
        # Opening section - gentle start
        ([1], 0.3),      # "Tale"
        ([1, 2], 0.3),   # "as"
        ([1, 2, 3], 0.6), # "old as time"
        ([], 0.2),       # Brief pause
        
        ([3, 4], 0.3),   # "True"
        ([3, 4, 5], 0.3), # "as"
        ([3, 4, 5, 6], 0.6), # "it can be"
        ([], 0.2),       # Brief pause
        
        # Moving pattern for chorus feel
        ([1, 8], 0.3),   # "Barely"
        ([2, 7], 0.3),   # "even"
        ([3, 6], 0.6),   # "friends"
        ([], 0.2),       # Brief pause
        
        ([4, 5], 0.3),   # "Then"
        ([3, 6], 0.3),   # "somebody"
        ([2, 7], 0.6),   # "bends"
        ([], 0.2),       # Brief pause
        
        # Big finale
        ([1, 3, 5, 7], 0.3),  # "Unexpectedly"
        ([2, 4, 6, 8], 0.3),
        ([1, 2, 3, 4, 5, 6, 7, 8], 0.6),  # Full chord
        ([], 0.3),
        
        # Final chord with sustain
        ([1, 2, 3, 4, 5, 6, 7, 8], 0.8),  # "Beauty and the Beast"
        ([], 0.3),
        
        # Gentle ending
        ([1], 0.2),
        ([2], 0.2),
        ([3], 0.2),
        ([4], 0.2),
        ([5], 0.2),
        ([6], 0.2),
        ([7], 0.2),
        ([8], 0.6),
        ([], 0.2),
    ]
    
    # Play the pattern
    for relays, duration in pattern:
        # Turn specified relays on
        for relay in relays:
            run_command(f"8relind {BOARD_ID} write {relay} on")
        
        # Wait for the specified duration
        time.sleep(duration)
        
        # Turn all relays off
        for relay in range(1, 9):
            run_command(f"8relind {BOARD_ID} write {relay} off")
        
        # Small pause between notes
        time.sleep(0.05)
    
    print("🎵 Beauty and the Beast pattern complete! 🎵")

# Print instructions
print("=== Rapid Relay Controller ===")
print("Press keys 1-8 to activate individual relays")
print("Press * to activate ALL relays simultaneously")
print("Press m for a musical easter egg")
print("Press b for Beauty and the Beast pattern")
print("Each relay will fire once when activated")
print("Press Ctrl+C to exit")
print("=============================")

# Main loop
try:
    while True:
        # Simple input
        key = input("Enter relay (1-8, * for all, m for music, b for Beauty and Beast): ")
        
        # Check for valid input
        if key in ['1', '2', '3', '4', '5', '6', '7', '8']:
            rapid_toggle_relay(int(key))
        elif key == '*':
            rapid_toggle_all_relays()
        elif key.lower() == 'm':
            play_music_pattern()
        elif key.lower() == 'b':
            play_beauty_and_beast()
        elif key.lower() in ['q', 'quit', 'exit']:
            break
        else:
            print("Please enter 1-8, * for all relays, m for music, or b for Beauty and Beast")
except KeyboardInterrupt:
    print("\nExiting...")

# Turn off all relays on exit
print("Turning all relays off...")
for i in range(1, 9):
    run_command(f"8relind {BOARD_ID} write {i} off")

print("Goodbye!")