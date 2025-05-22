import socket
import json
import time
from logger import Logger  # zakładamy, że logger.py istnieje
from network.config import load_config

class NetworkClient:
    def __init__(self, host: str = None, port: int = None, timeout: float = 5.0, retries: int = 3):
        config = load_config().get("client", {})
        self.host = host or config.get("host", "localhost")
        self.port = port or config.get("port", 5000)
        self.timeout = timeout or config.get("timeout", 5.0)
        self.retries = retries or config.get("retries", 3)
        self.socket = None
        self.logger = Logger("client_log.json")

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))
        self.logger.log_info("Połączono z serwerem.")

    def send(self, data: dict) -> bool:
        message = self._serialize(data)
        for attempt in range(self.retries):
            try:
                self.connect()
                self.socket.sendall(message)
                response = self.socket.recv(1024).decode("utf-8").strip()
                if response == "ACK":
                    self.logger.log_info(f"Wysłano dane: {data}")
                    self.socket.close()
                    return True
                else:
                    self.logger.log_error(f"Brak ACK. Odpowiedź: {response}")
            except Exception as e:
                self.logger.log_error(f"Błąd wysyłania: {e}")
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

    def _deserialize(self, raw: bytes) -> dict:
        return json.loads(raw.decode("utf-8"))
