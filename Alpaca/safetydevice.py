import requests

class SafetyDevice:
    """
    A device class for a safety monitor, used in astronomical setups.
    """

    def __init__(self):
        self.connected = False
        self.issafe = False
        self.safety_url = "http://localhost:5000/is_safe"  # URL of your Flask endpoint

    def connect(self):
        """
        Connects to the Safety Monitor.
        """
        self.connected = True

    def disconnect(self):
        """
        Disconnects from the Safety Monitor.
        """
        if self.connected:
            self.connected = False

    def is_safe(self):
        """
        Returns True if the safety monitor is safe, False otherwise.
        """
        if self.connected:
            try:
                response = requests.get(self.safety_url)
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                self.issafe = response.text.lower() == 'true'  # Convert response to boolean
                return self.issafe
            except requests.RequestException as e:
                print(f"Error querying safety status: {e}")
                return False
        else:
            print("Safety Device is not connected.")
            return False
