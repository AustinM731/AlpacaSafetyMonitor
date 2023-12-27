class SafetyDevice:
    """
    A device class for a safety monitor, used in astronomical setups.
    """

    def __init__(self):
        self.connected = False
        self.issafe = False

    def connect(self):
        """
        Connects to Safety Monitor.
        """
        self.connected = True

    def disconnect(self):
        """
        Disconnects from Safety Monitor.
        """
        if self.connected:
            self.connected = False
