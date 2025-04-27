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

def relay_mapping(relay_num):
    """Map keyboard input number to actual relay number based on calibration order"""
    mapping = {
        1: 4,  # Key 1 triggers relay 4
        2: 1,  # Key 2 triggers relay 1
        3: 3,  # Key 3 triggers relay 3
        4: 8,  # Key 4 triggers relay 8
        5: 5,  # Key 5 is still skipped
        6: 7,  # Key 6 triggers relay 7
        7: 2,  # Key 7 triggers relay 2
        8: 6   # Key 8 triggers relay 6
    }
    # Skip relay 5 regardless of mapping
    if relay_num == 5:
        return 0  # Return invalid relay number to skip
    return mapping.get(relay_num, relay_num)

def rapid_toggle_relay(relay_num):
    """Fire relay once instead of toggling repeatedly"""
    # Map the input relay number to the actual relay number
    actual_relay = relay_mapping(relay_num)
    
    # Skip if mapping returned 0 (invalid relay)
    if actual_relay == 0:
        print(f"\nSkipping relay {relay_num} as requested...")
        return
        
    print(f"\nActivating relay {relay_num} (mapped to actual relay {actual_relay})...")
    
    # Turn ON
    run_command(f"8relind {BOARD_ID} write {actual_relay} on")
    time.sleep(TOGGLE_DELAY)
    
    # Turn OFF
    run_command(f"8relind {BOARD_ID} write {actual_relay} off")
    
    print(f"Relay {relay_num} (mapped to {actual_relay}) fired once")

def rapid_toggle_all_relays():
    """Fire all relays once instead of toggling repeatedly"""
    print(f"\nActivating ALL relays once (except relay 5)...")
    
    # Define the relays to activate (excluding 5)
    relay_inputs = [1, 2, 3, 4, 6, 7, 8]
    active_relays = []
    
    # Turn all mapped relays ON
    for relay in relay_inputs:
        actual_relay = relay_mapping(relay)
        if actual_relay != 0:  # Skip invalid relays
            run_command(f"8relind {BOARD_ID} write {actual_relay} on")
            active_relays.append(actual_relay)
    time.sleep(TOGGLE_DELAY)
    
    # Turn all mapped relays OFF
    for actual_relay in active_relays:
        run_command(f"8relind {BOARD_ID} write {actual_relay} off")
    
    print(f"All relays fired once (except relay 5)")

def play_music_pattern():
    """Play a musical pattern on all relays as an easter egg"""
    print("\n🎵 Playing musical pattern on relays! 🎵")
    
    # Simple musical pattern (updated to exclude relay 5)
    pattern = [
        # Format: ([relays to activate], duration)
        ([1, 3, 7], 0.2),  # Alternating pattern (removed 5)
        ([2, 4, 6, 8], 0.2),  # Alternating pattern
        ([1, 2, 3, 4, 6, 7, 8], 0.3),  # All relays except 5
        ([1, 8], 0.15),  # Outer relays
        ([2, 7], 0.15),  # Moving inward
        ([3, 6], 0.15),  # Moving inward
        ([4], 0.15),  # Inner relay (removed 5)
        ([4], 0.15),  # Inner relay again (removed 5)
        ([3, 6], 0.15),  # Moving outward
        ([2, 7], 0.15),  # Moving outward
        ([1, 8], 0.15),  # Outer relays
        ([1, 2, 3, 4, 6, 7, 8], 0.1),  # Quick all on except 5
        ([], 0.1),  # All off
        ([1, 2, 3, 4, 6, 7, 8], 0.1),  # Quick all on except 5
        ([], 0.1),  # All off
        ([1, 2, 3, 4, 6, 7, 8], 0.3),  # Final all on except 5
        ([], 0.2),  # Final all off
    ]
    
    # Play the pattern
    for relays, duration in pattern:
        active_relays = []
        
        # Turn specified relays on (using mapping)
        for relay in relays:
            actual_relay = relay_mapping(relay)
            if actual_relay != 0:  # Skip invalid relays
                run_command(f"8relind {BOARD_ID} write {actual_relay} on")
                active_relays.append(actual_relay)
        
        # Wait for the specified duration
        time.sleep(duration)
        
        # Turn all active relays off
        for actual_relay in active_relays:
            run_command(f"8relind {BOARD_ID} write {actual_relay} off")
        
        # Small pause between notes
        time.sleep(0.05)
    
    print("🎵 Musical pattern complete! 🎵")

def play_beauty_and_beast():
    """Play a Beauty and the Beast inspired pattern on the relays"""
    print("\n🎵 Playing Beauty and the Beast pattern on relays! 🎵")
    
    # Beauty and the Beast inspired pattern (updated to exclude relay 5)
    # Creates a waltz-like pattern with the relays
    pattern = [
        # Opening section - gentle start
        ([1], 0.3),      # "Tale"
        ([1, 2], 0.3),   # "as"
        ([1, 2, 3], 0.6), # "old as time"
        ([], 0.2),       # Brief pause
        
        ([3, 4], 0.3),   # "True"
        ([3, 4], 0.3),   # "as" (removed 5)
        ([3, 4, 6], 0.6), # "it can be" (removed 5)
        ([], 0.2),       # Brief pause
        
        # Moving pattern for chorus feel
        ([1, 8], 0.3),   # "Barely"
        ([2, 7], 0.3),   # "even"
        ([3, 6], 0.6),   # "friends"
        ([], 0.2),       # Brief pause
        
        ([4], 0.3),      # "Then" (removed 5)
        ([3, 6], 0.3),   # "somebody"
        ([2, 7], 0.6),   # "bends"
        ([], 0.2),       # Brief pause
        
        # Big finale
        ([1, 3, 7], 0.3),  # "Unexpectedly" (removed 5)
        ([2, 4, 6, 8], 0.3),
        ([1, 2, 3, 4, 6, 7, 8], 0.6),  # Full chord (removed 5)
        ([], 0.3),
        
        # Final chord with sustain
        ([1, 2, 3, 4, 6, 7, 8], 0.8),  # "Beauty and the Beast" (removed 5)
        ([], 0.3),
        
        # Gentle ending
        ([1], 0.2),
        ([2], 0.2),
        ([3], 0.2),
        ([4], 0.2),
        # Skip 5
        ([6], 0.2),
        ([7], 0.2),
        ([8], 0.6),
        ([], 0.2),
    ]
    
    # Play the pattern
    for relays, duration in pattern:
        active_relays = []
        
        # Turn specified relays on (using mapping)
        for relay in relays:
            actual_relay = relay_mapping(relay)
            if actual_relay != 0:  # Skip invalid relays
                run_command(f"8relind {BOARD_ID} write {actual_relay} on")
                active_relays.append(actual_relay)
        
        # Wait for the specified duration
        time.sleep(duration)
        
        # Turn all active relays off
        for actual_relay in active_relays:
            run_command(f"8relind {BOARD_ID} write {actual_relay} off")
        
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
# Directly turn off all physical relays 1-8 to ensure a clean state
for i in range(1, 9):
    run_command(f"8relind {BOARD_ID} write {i} off")

print("Goodbye!")