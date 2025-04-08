from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import threading
import os
import sys

# Check if running on Raspberry Pi or in development mode
try:
    import lib8relind as relays  # For the Sequent Microsystems 8-relay board
    DEV_MODE = False
except ImportError:
    print("Running in DEVELOPMENT MODE - hardware control is simulated")
    DEV_MODE = True

# Set up Flask application
app = Flask(__name__, static_folder='.')
CORS(app)  # Enable cross-origin requests

# Define relay pins/channels (1-8 for the 8relind board)
RELAY_CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]

# Solenoid activation time in seconds
ACTIVATION_TIME = 0.5

# Motor state tracking
motor_lock = threading.Lock()
current_motor = 0
# Track which motors have been activated (for direct keyboard control)
motors_activated = [False] * 8

# Initialize relays (set all to off)
def init_relays():
    if not DEV_MODE:
        # Check if the relay board is detected (stack level 0)
        try:
            relays.check(0)
            print("8-Relay Industrial board detected")
            
            # Turn off all relays
            for channel in RELAY_CHANNELS:
                relays.set(0, channel, 0)  # stack, channel, state(0=off)
                
        except Exception as e:
            print(f"Error initializing relay board: {e}")
            print("Make sure the 8-Relay Industrial board is properly connected")
    else:
        print("[SIMULATION] Initializing all relays to OFF state")

# Activate a specific relay/solenoid
def activate_relay(motor_index, duration=ACTIVATION_TIME):
    if motor_index < 0 or motor_index >= len(RELAY_CHANNELS):
        print(f"Invalid motor index: {motor_index}")
        return
        
    channel = RELAY_CHANNELS[motor_index]
    
    if not DEV_MODE:
        try:
            # Turn on the relay
            relays.set(0, channel, 1)  # stack, channel, state(1=on)
            
            # Keep activated for specified duration
            time.sleep(duration)
            
            # Turn off the relay
            relays.set(0, channel, 0)  # stack, channel, state(0=off)
        except Exception as e:
            print(f"Error controlling relay {channel}: {e}")
    else:
        # Simulation mode - just print and sleep
        print(f"[SIMULATION] Activating relay {motor_index} on channel {channel} for {duration} seconds")
        time.sleep(duration)
        print(f"[SIMULATION] Deactivating relay {motor_index}")

@app.route('/api/activate', methods=['POST'])
def activate_motor():
    global current_motor, motors_activated
    
    # Get data from request
    data = request.get_json()
    motor_index = data.get('motor', 0)
    
    with motor_lock:
        # Check if motor index is valid
        if motor_index < 0 or motor_index >= len(RELAY_CHANNELS):
            return jsonify({'success': False, 'message': 'Invalid motor index'}), 400
        
        # Activate the requested relay in a separate thread to not block the response
        threading.Thread(target=activate_relay, args=(motor_index,)).start()
        
        # Mark this motor as activated
        motors_activated[motor_index] = True
        
        # If this is a sequential activation (matches current_motor), increment the counter
        if motor_index == current_motor:
            current_motor = current_motor + 1
        # Otherwise, check if all motors up to the highest activated one are activated
        else:
            # For keyboard mode tracking, we'll just count how many have been activated
            # since direct keyboard might trigger them out of order
            current_motor = sum(1 for m in motors_activated if m)
        
        return jsonify({
            'success': True, 
            'message': f'Motor {motor_index} activated',
            'currentMotor': current_motor,
            'motorsActivated': motors_activated
        })

@app.route('/api/reset', methods=['POST'])
def reset_system():
    global current_motor, motors_activated
    
    with motor_lock:
        # Reset the current motor counter and activation status
        current_motor = 0
        motors_activated = [False] * 8
        
        if not DEV_MODE:
            # For safety, ensure all relays are off
            for channel in RELAY_CHANNELS:
                try:
                    relays.set(0, channel, 0)  # stack, channel, state(0=off)
                except Exception as e:
                    print(f"Error resetting relay {channel}: {e}")
        else:
            print("[SIMULATION] System fully reset - all relays confirmed OFF")
        
        return jsonify({'success': True, 'message': 'System reset complete'})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'currentMotor': current_motor,
        'motorsActivated': motors_activated
    })

# Serve the static HTML file
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# For direct browser access to other static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Initialize and start the server
if __name__ == '__main__':
    # Initialize relays on startup
    init_relays()
    
    print("Starting Beauty and the Beast Petal Ejector Server...")
    if DEV_MODE:
        print("DEVELOPMENT MODE: Hardware control is simulated")
    else:
        print("PRODUCTION MODE: Hardware control is active")
    
    # Get IP address
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        print(f"Access the application at http://{ip_address}:8080")
    except:
        print("Access the application at http://YOUR_PI_IP:8080")
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=8080, debug=False)  # Set debug=False for production