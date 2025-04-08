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