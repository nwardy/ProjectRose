#!/bin/bash

# Beauty and the Beast Petal Controller Installation Script
echo "================================================="
echo "  Beauty and the Beast Petal Controller Setup"
echo "================================================="
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Warning: Not running as root. Some commands may fail.${NC}"
  echo "Consider running with sudo if you encounter permission errors."
  echo
fi

# Function to print step information
print_step() {
  echo -e "${GREEN}[STEP]${NC} $1"
}

# Function to handle errors
handle_error() {
  echo -e "${RED}[ERROR]${NC} $1"
  echo "The installation has been interrupted."
  exit 1
}

# Step 1: Update system packages
print_step "Updating system packages..."
apt update || handle_error "Failed to update package list"
apt install -y python3 python3-pip nginx git || handle_error "Failed to install required packages"

# Step 2: Install Python dependencies
print_step "Installing Python dependencies..."
pip3 install flask flask-cors || handle_error "Failed to install Python dependencies"

# Step 3: Install relay library (if not already installed)
print_step "Installing relay library..."
if [ ! -d "8relind-rpi" ]; then
  git clone https://github.com/SequentMicrosystems/8relind-rpi.git || handle_error "Failed to download relay library"
  (cd 8relind-rpi/ && make install) || handle_error "Failed to install relay library"
  (cd 8relind-rpi/python/8relind/ && python3 setup.py install) || handle_error "Failed to install Python bindings for relay library"
else
  echo "Relay library already installed, skipping."
fi

# Step 4: Create required directories
print_step "Setting up web directories..."
INSTALL_DIR=$(pwd)
mkdir -p /var/www/html/petal-controller || handle_error "Failed to create web directory"
ln -sf $INSTALL_DIR/* /var/www/html/petal-controller/ || handle_error "Failed to link project files"

# Step 5: Configure nginx
print_step "Configuring web server..."
cat > /etc/nginx/sites-available/petal-controller << EOF
server {
    listen 80 default_server;
    root /var/www/html/petal-controller;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 90;
    }
}
EOF

ln -sf /etc/nginx/sites-available/petal-controller /etc/nginx/sites-enabled/ || handle_error "Failed to enable nginx configuration"
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx || handle_error "Failed to restart nginx"

# Step 6: Set up systemd service
print_step "Creating service for auto-start..."
cat > /etc/systemd/system/petal-controller.service << EOF
[Unit]
Description=Beauty and the Beast Petal Controller
After=network.target

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/app.py
WorkingDirectory=$INSTALL_DIR
Restart=always
User=$(whoami)

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload || handle_error "Failed to reload systemd configuration"
systemctl enable petal-controller || handle_error "Failed to enable service"

# Step 7: Make scripts executable
print_step "Making scripts executable..."
chmod +x app.py || handle_error "Failed to make scripts executable"

# Step 8: Create a local launcher shortcut
print_step "Creating desktop shortcut..."
mkdir -p /home/$(logname)/Desktop
cat > /home/$(logname)/Desktop/petal-controller.desktop << EOF
[Desktop Entry]
Type=Application
Name=Petal Controller
Comment=Beauty and the Beast Petal Controller
Exec=chromium-browser http://localhost:80
Icon=applications-electronics
Terminal=false
Categories=Utility;
EOF
chmod +x /home/$(logname)/Desktop/petal-controller.desktop || handle_error "Failed to make desktop shortcut executable"

# Step 9: Complete!
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo
echo "To control your petals:"
echo
echo "1. Using a web browser from any device on the same network:"
echo "   http://$(hostname -I | awk '{print $1}')"
echo
echo "2. With a keyboard (select Keyboard Mode from the main screen):"
echo "   - X or spacebar: Drop next petal"
echo "   - Keys 1-8: Activate specific motors"
echo "   - R: Reset (after all petals dropped)"
echo
echo "The controller will automatically start on boot."
echo
echo "You can also open the controller by clicking the shortcut on the desktop."
echo

# Ask to run now
read -p "Would you like to start the controller now? (y/n): " choice
case "$choice" in 
  y|Y ) 
    systemctl start petal-controller
    echo "Controller started! Access it at: http://$(hostname -I | awk '{print $1}')"
    echo "Or use the desktop shortcut to open it in a browser."
    ;;
  * ) 
    echo "You can start it later with: sudo systemctl start petal-controller"
    ;;
esac

echo
echo "Enjoy your show!"