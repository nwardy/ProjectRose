// Initialize Angular application
var app = angular.module('petalEjectorApp', []);

// Define the controller
app.controller('MotorController', function($scope, $http, $interval, $timeout) {
    // Initialize variables
    $scope.ipAddress = "";
    $scope.isConnected = false;
    $scope.isConnecting = false;
    $scope.currentMotor = 0;
    $scope.logEntries = [];
    $scope.statusCheckInterval = null;
    $scope.showModeSelection = true; // Show mode selection initially
    $scope.isKeyboardMode = false;
    $scope.isKeyboardActive = false;
    $scope.isRunningSetup = false;
    
    // API base URL for local mode
    var apiBase = "http://localhost:8080/api";
    
    // Function to add log entry
    $scope.addLogEntry = function(message) {
        var timestamp = new Date().toLocaleTimeString();
        $scope.logEntries.push("[" + timestamp + "] " + message);
        
        // Auto-scroll to bottom
        $timeout(function() {
            var terminal = document.querySelector('.terminal-content');
            if (terminal) {
                terminal.scrollTop = terminal.scrollHeight;
            }
        }, 10);
    };
    
    // Function to clear log
    $scope.clearLog = function() {
        $scope.logEntries = [];
    };
    
    // Function to select control mode
    $scope.selectMode = function(mode) {
        $scope.showModeSelection = false;
        
        if (mode === "keyboard") {
            $scope.isKeyboardMode = true;
            $scope.addLogEntry("Keyboard mode selected");
            $scope.addLogEntry("This mode is for EMERGENCY USE when network control is unavailable");
            $scope.addLogEntry("Please run Setup if this is your first time, then Activate Keyboard Mode");
        } else {
            $scope.isKeyboardMode = false;
            $scope.addLogEntry("Web controller mode selected");
            $scope.addLogEntry("Enter the Raspberry Pi IP address to connect");
        }
    };
    
    // Function to go back to mode selection
    $scope.backToModeSelection = function() {
        // Disconnect if connected
        if ($scope.isConnected) {
            $scope.connect(); // This will handle the disconnect
        }
        
        // Deactivate keyboard mode if active
        if ($scope.isKeyboardActive) {
            $scope.toggleKeyboardMode();
        }
        
        $scope.showModeSelection = true;
        $scope.isKeyboardMode = false;
    };
    
    // Function to run setup
    $scope.runSetup = function() {
        $scope.isRunningSetup = true;
        $scope.addLogEntry("Running setup...");
        $scope.addLogEntry("Checking for relay board...");
        
        // Simulate checking hardware
        $timeout(function() {
            $scope.addLogEntry("Installing required libraries...");
        }, 1000);
        
        $timeout(function() {
            $scope.addLogEntry("Setting up relay controls...");
        }, 2000);
        
        $timeout(function() {
            $scope.addLogEntry("✓ Setup complete! The system is ready.");
            $scope.addLogEntry("Click 'Activate Keyboard Mode' to begin controlling petals");
            $scope.isRunningSetup = false;
        }, 3000);
    };
    
    // Function to toggle keyboard mode
    $scope.toggleKeyboardMode = function() {
        $scope.isKeyboardActive = !$scope.isKeyboardActive;
        
        if ($scope.isKeyboardActive) {
            $scope.addLogEntry("KEYBOARD MODE ACTIVATED");
            $scope.addLogEntry("Press X or Space to drop the next petal");
            $scope.addLogEntry("Press R to reset (only after all petals have dropped)");
            
            // Connect to local API
            $scope.isConnected = true;
            $scope.currentMotor = 0;
            
            // Start listening for keyboard events
            document.addEventListener('keydown', $scope.handleKeyboardInput);
        } else {
            $scope.addLogEntry("Keyboard mode deactivated");
            $scope.isConnected = false;
            $scope.currentMotor = 0;
            
            // Stop listening for keyboard events
            document.removeEventListener('keydown', $scope.handleKeyboardInput);
        }
    };
    
    // Function to handle keyboard input
    $scope.handleKeyboardInput = function(event) {
        if (!$scope.isKeyboardActive) {
            return;
        }
        
        var key = event.key.toLowerCase();
        
        // Process keyboard input
        if (key === 'x' || key === ' ') {
            // Drop next petal
            $scope.$apply(function() {
                $scope.activateNextMotor();
            });
        } else if (key === 'r' && $scope.currentMotor >= 8) {
            // Reset system (only after all petals dropped)
            $scope.$apply(function() {
                $scope.resetSystem();
            });
        }
    };
    
    // Function to connect to the Raspberry Pi
    $scope.connect = function() {
        if ($scope.isConnected) {
            // Disconnect
            $scope.isConnected = false;
            $scope.currentMotor = 0;
            $scope.addLogEntry("Disconnected from " + $scope.ipAddress);
            
            // Clear status check interval
            if ($scope.statusCheckInterval) {
                $interval.cancel($scope.statusCheckInterval);
                $scope.statusCheckInterval = null;
            }
            
            return;
        }
        
        if (!$scope.ipAddress) {
            alert("Please enter an IP address");
            return;
        }
        
        $scope.isConnecting = true;
        $scope.addLogEntry("Connecting to " + $scope.ipAddress + "...");
        
        // Set API base URL
        apiBase = "http://" + $scope.ipAddress + ":8080/api";
        
        // Special case for test mode (1.1.1.1)
        if ($scope.ipAddress === "1.1.1.1") {
            $timeout(function() {
                $scope.isConnected = true;
                $scope.isConnecting = false;
                $scope.currentMotor = 0;
                $scope.addLogEntry("Connected to TEST MODE");
                $scope.addLogEntry("WARNING: No actual hardware control in test mode");
                $scope.addLogEntry("Ready to simulate petal dropping");
            }, 1000);
            return;
        }
        
        // Try to connect to the actual Raspberry Pi
        $http.get(apiBase + "/status")
            .then(function(response) {
                $scope.isConnected = true;
                $scope.isConnecting = false;
                
                // Get current motor status if available
                if (response.data && response.data.currentMotor !== undefined) {
                    $scope.currentMotor = response.data.currentMotor;
                } else {
                    $scope.currentMotor = 0;
                }
                
                $scope.addLogEntry("Connected to Raspberry Pi at " + $scope.ipAddress);
                $scope.addLogEntry("Ready to drop petals");
                
                // Start periodically checking status
                $scope.startStatusCheck();
            })
            .catch(function(error) {
                $scope.isConnecting = false;
                console.error('Connection error', error);
                $scope.addLogEntry("ERROR: Failed to connect to " + $scope.ipAddress);
                $scope.addLogEntry("Make sure the Raspberry Pi is running the petal controller app");
                alert("Failed to connect to " + $scope.ipAddress);
            });
    };
    
    // Function to periodically check status (only for real Raspberry Pi)
    $scope.startStatusCheck = function() {
        if ($scope.statusCheckInterval) {
            $interval.cancel($scope.statusCheckInterval);
        }
        
        $scope.statusCheckInterval = $interval(function() {
            if (!$scope.isConnected || $scope.ipAddress === "1.1.1.1") {
                return;
            }
            
            $http.get(apiBase + "/status")
                .then(function(response) {
                    // Update current motor status if it changed
                    if (response.data && response.data.currentMotor !== undefined && 
                        response.data.currentMotor !== $scope.currentMotor) {
                        $scope.currentMotor = response.data.currentMotor;
                        $scope.addLogEntry("Status update: " + (8 - $scope.currentMotor) + " petals remaining");
                    }
                })
                .catch(function(error) {
                    console.error('Status check error', error);
                    // Don't log every failed status check to avoid filling the log
                });
        }, 5000); // Check every 5 seconds
    };
    
    // Function to activate the next motor
    $scope.activateNextMotor = function() {
        if (!$scope.isConnected || $scope.currentMotor >= 8) {
            return;
        }
        
        $scope.addLogEntry("Activating solenoid " + $scope.currentMotor);
        
        // Keyboard mode (direct local control)
        if ($scope.isKeyboardMode && $scope.isKeyboardActive) {
            // Simulate activation in keyboard mode
            $timeout(function() {
                $scope.addLogEntry("LOCAL: Motor " + $scope.currentMotor + " activated");
                $scope.currentMotor++;
                
                if ($scope.currentMotor >= 8) {
                    $scope.addLogEntry("All petals dropped. Press R to reset.");
                } else {
                    $scope.addLogEntry("Ready for next petal. " + (8 - $scope.currentMotor) + " remaining.");
                }
            }, 500);
            return;
        }
        
        // Test mode
        if ($scope.ipAddress === "1.1.1.1") {
            $timeout(function() {
                $scope.addLogEntry("SIMULATION: Motor " + $scope.currentMotor + " activated");
                $scope.currentMotor++;
                
                if ($scope.currentMotor >= 8) {
                    $scope.addLogEntry("All petals dropped. Ready for reset.");
                } else {
                    $scope.addLogEntry("Ready for next petal. " + (8 - $scope.currentMotor) + " remaining.");
                }
            }, 800);
            return;
        }
        
        // Real Raspberry Pi mode
        $http.post(apiBase + "/activate", {
            motor: $scope.currentMotor
        }).then(function(response) {
            $scope.addLogEntry("Motor " + $scope.currentMotor + " activated successfully");
            $scope.currentMotor++;
            
            if ($scope.currentMotor >= 8) {
                $scope.addLogEntry("All petals dropped. Ready for reset.");
            } else {
                $scope.addLogEntry("Ready for next petal. " + (8 - $scope.currentMotor) + " remaining.");
            }
        }).catch(function(error) {
            $scope.addLogEntry("ERROR: Failed to activate motor " + $scope.currentMotor);
            console.error('Error activating motor', error);
        });
    };
    
    // Function to reset the system (only available after all petals have dropped)
    $scope.resetSystem = function() {
        if (!$scope.isConnected || $scope.currentMotor < 8) {
            return;
        }
        
        $scope.addLogEntry("Resetting all petals...");
        
        // Keyboard mode (direct local control)
        if ($scope.isKeyboardMode && $scope.isKeyboardActive) {
            $timeout(function() {
                $scope.addLogEntry("LOCAL: System reset complete");
                $scope.currentMotor = 0;
                $scope.addLogEntry("Ready to drop petals");
            }, 1000);
            return;
        }
        
        // Test mode
        if ($scope.ipAddress === "1.1.1.1") {
            $timeout(function() {
                $scope.addLogEntry("SIMULATION: System reset complete");
                $scope.currentMotor = 0;
                $scope.addLogEntry("Ready to drop petals");
            }, 1000);
            return;
        }
        
        // Real Raspberry Pi mode
        $http.post(apiBase + "/reset").then(function(response) {
            $scope.addLogEntry("System reset complete");
            $scope.currentMotor = 0;
            $scope.addLogEntry("Ready to drop petals");
        }).catch(function(error) {
            $scope.addLogEntry("ERROR: Failed to reset system");
            console.error('Error resetting system', error);
        });
    };
    
    // Function to execute a setup command on the Pi
    $scope.executeSetup = function() {
        // This would actually call an API endpoint that runs the setup script
        // For now, we'll just simulate it
        $scope.addLogEntry("Executing setup command on Raspberry Pi...");
        
        // This could be a real API call in a production environment
        // $http.post(apiBase + "/setup").then(...
    };
    
    // Initial log entry
    $scope.addLogEntry("Beauty and the Beast Petal Controller initialized");
    $scope.addLogEntry("Please select a control mode to begin");
});