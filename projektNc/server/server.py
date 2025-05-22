import socket
import json
import threading
import sys
from network.config import load_config

class NetworkServer:
    def __init__(self, port: int = None):
        config = load_config().get("server", {})
        self.port = port or config.get("port", 5000)

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(5)
        print(f"[INFO] Serwer nasłuchuje na porcie {self.port}...")

        try:
            while True:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_socket,)).start()
        except KeyboardInterrupt:
            print("\n[INFO] Serwer zakończył działanie.")
        finally:
            server_socket.close()

    def _handle_client(self, client_socket):
        try:
            data = b""
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                data += chunk
                if b"\n" in chunk:
                    break

            message = json.loads(data.decode("utf-8"))
            print("[INFO] Odebrano dane:")
            for k, v in message.items():
                print(f"  {k}: {v}")

            client_socket.sendall(b"ACK\n")
        except Exception as e:
            print(f"[ERROR] Błąd obsługi klienta: {e}", file=sys.stderr)
        finally:
            client_socket.close()
