#!/usr/bin/env python3
import os
import sys
import time
import curses
import subprocess
from pathlib import Path

def display_title(stdscr, selected_option):
    """Display the main menu title screen"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Display title
    title = "Beauty and the Beast Rose Petal Controller"
    x = w//2 - len(title)//2
    stdscr.addstr(2, x, title, curses.A_BOLD)
    
    # Display subtitle
    subtitle = "Fallback Control System"
    x = w//2 - len(subtitle)//2
    stdscr.addstr(4, x, subtitle)
    
    # Display options
    options = [
        "1. Start Web Server (Normal Operation)",
        "2. Keyboard Control Mode (Emergency Use)",
        "3. Exit"
    ]
    
    for i, option in enumerate(options):
        x = w//2 - len(option)//2
        y = 7 + i
        mode = curses.A_REVERSE if i == selected_option else curses.A_NORMAL
        stdscr.addstr(y, x, option, mode)
    
    # Display key instructions
    instructions = "Use UP/DOWN arrows to select, ENTER to confirm"
    x = w//2 - len(instructions)//2
    stdscr.addstr(h-3, x, instructions)
    
    # Display version
    version = "v1.0.0"
    stdscr.addstr(h-1, w-len(version)-1, version)
    
    stdscr.refresh()

def start_web_server():
    """Start the web server for normal operation"""
    os.system('clear')
    print("=== Starting Beauty and the Beast Petal Controller ===")
    print("The web interface is now running.")
    
    # Display IP address
    ip = get_ip_address()
    if ip:
        print(f"\nAccess the controller from any device at: http://{ip}")
    else:
        print("\nCould not determine IP address.")
        print("Try accessing the controller at http://[raspberry-pi-ip]")
    
    print("\nPress Ctrl+C to stop the server and return to the menu.\n")
    
    try:
        # Start app.py
        os.system('python3 app.py')
    except KeyboardInterrupt:
        print("\nServer stopped.")
    
    input("\nPress Enter to return to the main menu...")

def keyboard_mode():
    """Direct keyboard control mode for the petals"""
    os.system('clear')
    print("=== Beauty and the Beast Petal Dropper - Direct Keyboard Control ===")
    print("\nThis mode allows direct control when network/SSH is unavailable.")
    print("Each press of the X key will drop one petal in sequence.")
    print("\nINSTRUCTIONS:")
    print("  - Press X to drop the next petal")
    print("  - Press R to reset all petals (only after all 8 petals have dropped)")
    print("  - Press Q to quit and return to the main menu")
    print("\n--------------------------------------------------------------")
    
    # Try to import the relay functions from app.py
    try:
        # Add the current directory to the Python path
        sys.path.append(os.getcwd())
        
        # Try to import from app.py
        from app import init_relays, activate_relay, RELAY_CHANNELS
        dev_mode = False
        print("\nHardware control initialized!")
    except ImportError:
        # Simulation mode
        print("\nWARNING: Relay library not found. Running in SIMULATION mode.")
        dev_mode = True
        
        # Define simulated functions
        def init_relays():
            print("[SIMULATION] Initializing all relays to OFF state")
        
        def activate_relay(motor_index, duration=0.5):
            print(f"[SIMULATION] Activating relay {motor_index}")
            time.sleep(duration)
            print(f"[SIMULATION] Deactivating relay {motor_index}")
        
        RELAY_CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
    
    # Initialize relays
    init_relays()
    
    # Track current state
    current_motor = 0
    
    # Main keyboard loop
    print("\nReady to control petals!")
    print(f"Petals remaining: {8 - current_motor}")
    
    while True:
        # Get keypress
        key = input("\n> Press key (x/r/q): ").lower()
        
        if key == 'x':
            if current_motor >= 8:
                print("All petals have been dropped. Press R to reset.")
            else:
                print(f"Activating solenoid {current_motor}...")
                activate_relay(current_motor, 0.5)
                current_motor += 1
                print(f"Petal dropped! Petals remaining: {8 - current_motor}")
        
        elif key == 'r':
            if current_motor < 8:
                print("Cannot reset until all petals have been dropped.")
            else:
                print("Resetting all petals...")
                current_motor = 0
                print("Reset complete. Petals remaining: 8")
        
        elif key == 'q':
            print("Exiting keyboard control mode...")
            break
        
        else:
            print("Unknown command. Use X to drop petal, R to reset, Q to quit.")

def get_ip_address():
    """Get the Raspberry Pi's IP address"""
    try:
        cmd = "hostname -I | awk '{print $1}'"
        ip = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return ip
    except:
        return None

def main(stdscr):
    # Set up curses
    curses.curs_set(0)  # Hide cursor
    stdscr.keypad(True)  # Enable keypad mode
    
    # Initialize selected option
    current_option = 0
    
    # Main menu loop
    while True:
        display_title(stdscr, current_option)
        
        # Get key
        key = stdscr.getch()
        
        # Handle key
        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < 2:
            current_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Exit curses mode
            curses.endwin()
            
            # Handle selected option
            if current_option == 0:
                # Start Web Server
                start_web_server()
            elif current_option == 1:
                # Keyboard Control Mode
                keyboard_mode()
            elif current_option == 2:
                # Exit
                os.system('clear')
                print("Exiting Beauty and the Beast Petal Controller.")
                return
            
            # Restore curses mode
            stdscr = curses.initscr()
            curses.curs_set(0)
            stdscr.keypad(True)

if __name__ == "__main__":
    # Check if running directly on the Pi (in case SSH fails)
    try:
        # Launch curses application
        curses.wrapper(main)
    except Exception as e:
        print(f"Error: {e}")
        print("If you're seeing this error, try running in basic keyboard mode:")
        print("python3 -c 'from main import keyboard_mode; keyboard_mode()'")