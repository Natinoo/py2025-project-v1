import socket
import json
import time
from network.config import load_config

class NetworkClient:
    def __init__(self, host: str = None, port: int = None, timeout: float = 5.0, retries: int = 3):
        config = load_config().get("client", {})
        self.host = host or config.get("host", "localhost")
        self.port = port or config.get("port", 5001)
        self.timeout = timeout or config.get("timeout", 5.0)
        self.retries = retries or config.get("retries", 3)
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            print(f"Attempting to connect to {self.host}:{self.port}")  # Debug
            self.socket.connect((self.host, self.port))
            print("Connection successful")  # Debug
        except Exception as e:
            print(f"Connection failed: {e}")
            raise

    def send(self, data: dict) -> bool:
        message = self._serialize(data)
        for attempt in range(self.retries):
            try:
                self.connect()
                self.socket.sendall(message)
                response = self.socket.recv(1024).decode("utf-8").strip()
                if response == "ACK":
                    return True
            except Exception as e:
                print(f"Error sending data: {e}")
            finally:
                self.close()
                time.sleep(1)
        return False

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def _serialize(self, data: dict) -> bytes:
        return (json.dumps(data) + "\n").encode("utf-8")