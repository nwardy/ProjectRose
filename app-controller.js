// Make sure app is defined
var app = app || angular.module('petalEjectorApp', []);

// First, define the API service
app.service('ApiService', function($http) {
    var service = {};
    
    // Base URL for API calls
    service.baseUrl = "";
    
    // Set the base URL for the API service
    service.setBaseUrl = function(ipAddress) {
        service.baseUrl = "http://" + ipAddress + ":8080/api";
    };
    
    // Check connection to the Raspberry Pi
    service.checkConnection = function() {
        return $http.get(service.baseUrl + "/status");
    };
    
    // Activate a motor
    service.activateMotor = function(motorIndex) {
        return $http.post(service.baseUrl + "/activate", {
            motor: motorIndex
        });
    };
    
    // Reset the system
    service.resetSystem = function() {
        return $http.post(service.baseUrl + "/reset");
    };
    
    // Get system status
    service.getStatus = function() {
        return $http.get(service.baseUrl + "/status");
    };
    
    return service;
});

// Then define the controller
app.controller('MotorController', function($scope, $interval, $timeout, ApiService) {
    // Initialize variables
    $scope.ipAddress = "";
    $scope.isConnected = false;
    $scope.isConnecting = false;
    $scope.currentMotor = 0;
    $scope.logEntries = [];
    $scope.statusCheckInterval = null;
    
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
        
        // Set the base URL for the API service
        ApiService.setBaseUrl($scope.ipAddress);
        
        // Try to connect to the actual Raspberry Pi
        ApiService.checkConnection()
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
            
            ApiService.getStatus()
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
        ApiService.activateMotor($scope.currentMotor)
            .then(function(response) {
                $scope.addLogEntry("Motor " + $scope.currentMotor + " activated successfully");
                $scope.currentMotor++;
                
                if ($scope.currentMotor >= 8) {
                    $scope.addLogEntry("All petals dropped. Ready for reset.");
                } else {
                    $scope.addLogEntry("Ready for next petal. " + (8 - $scope.currentMotor) + " remaining.");
                }
            })
            .catch(function(error) {
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
        ApiService.resetSystem()
            .then(function(response) {
                $scope.addLogEntry("System reset complete");
                $scope.currentMotor = 0;
                $scope.addLogEntry("Ready to drop petals");
            })
            .catch(function(error) {
                $scope.addLogEntry("ERROR: Failed to reset system");
                console.error('Error resetting system', error);
            });
    };
    
    // Initial log entry
    $scope.addLogEntry("Remote Petal Controller initialized");
    $scope.addLogEntry("Please enter a Raspberry Pi IP address to connect");
    $scope.addLogEntry("Use 1.1.1.1 for test mode (no actual hardware control)");
});