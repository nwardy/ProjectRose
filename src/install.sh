#!/bin/bash
# Installation script for ProjectRose Relay Controller

# Display banner
echo "================================================="
echo "       ProjectRose Relay Controller Setup        "
echo "       For Sequent Microsystems 8RELIND         "
echo "       Board ID: 7                              "
echo "================================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo && ! grep -q "raspberrypi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi."
    echo "The script will continue, but may not work correctly on this system."
    echo ""
fi

# Create directory for the application
echo "Creating application directory..."
mkdir -p ~/relay-controller
cd ~/relay-controller

# Check if Sequent Microsystems library is installed
echo "Checking for Sequent Microsystems 8RELIND library..."
if ! command -v 8relind &> /dev/null; then
    echo "8RELIND command not found. Installing..."
    
    # Install dependencies
    echo "Installing dependencies..."
    sudo apt-get update
    sudo apt-get install -y git build-essential python3-pip python3-dev

    # Clone and install the Sequent Microsystems repository
    echo "Cloning 8RELIND repository..."
    git clone https://github.com/SequentMicrosystems/8relind-rpi.git
    cd 8relind-rpi
    
    echo "Installing command line tool..."
    sudo make install
    
    cd ~/relay-controller
else
    echo "8RELIND library already installed."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install readchar

# Copy the controller script from the project directory
echo "Installing controller script..."
cp $(dirname "$0")/simple_relay_control.py ~/relay-controller/
chmod +x ~/relay-controller/simple_relay_control.py

# Create a launcher script for easy starting
cat > ~/relay-controller/start.sh << 'EOL'
#!/bin/bash
cd ~/relay-controller
python3 simple_relay_control.py "$@"
EOL

chmod +x ~/relay-controller/start.sh

# Create desktop shortcut if running on a desktop environment
if [ -d ~/Desktop ]; then
    cat > ~/Desktop/RelayController.desktop << 'EOL'
[Desktop Entry]
Type=Application
Name=Relay Controller
Comment=Control Sequent Microsystems 8RELIND board
Exec=bash -c "cd ~/relay-controller && ./start.sh"
Terminal=true
Categories=Utility;
EOL

    chmod +x ~/Desktop/RelayController.desktop
    echo "Desktop shortcut created."
fi

echo ""
echo "Installation complete!"
echo ""
echo "To start the controller:"
echo "  cd ~/relay-controller"
echo "  ./start.sh [board_id]"
echo ""
echo "The default board ID is 0 if not specified."
echo "Press keys 1-8 twice quickly to activate relays."