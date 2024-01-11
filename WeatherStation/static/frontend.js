document.addEventListener('DOMContentLoaded', function() {
    function updateSensorDisplay(data) {
        document.getElementById('ambientTemperature').textContent = data.ambient_temperature_f.toFixed(1);
        document.getElementById('skyTemperature').textContent = data.sky_temperature_f.toFixed(1);
        document.getElementById('humidity').textContent = data.humidity.toFixed(1);
        document.getElementById('cloudiness').textContent = data.cloudiness;
        document.getElementById('pressure').textContent = data.pressure_inhg.toFixed(1);
        document.getElementById('rain').textContent = data.rain ? 'Yes' : 'No';
    }

    function updateSafetyStatus(isSafe) {
        document.getElementById('safe').textContent = isSafe ? 'Safe' : 'Unsafe';
    }

    // Use window.location.hostname to get the current server's IP or domain
    const serverIP = window.location.hostname;
    const dataEndpoint = `http://${serverIP}:5000/data`;
    const safetyEndpoint = `http://${serverIP}:5000/is_safe`;

    fetch(dataEndpoint)
    .then(response => response.json())
    .then(data => {
        console.log('Sensor data:', data);
        updateSensorDisplay(data);
    })
    .catch(error => console.error('Error fetching sensor data:', error));

    fetch(safetyEndpoint)
    .then(response => response.json())
    .then(data => {
        console.log('Safety status:', data);
        updateSafetyStatus(data);
    })
    .catch(error => console.error('Error fetching safety status:', error));
});
