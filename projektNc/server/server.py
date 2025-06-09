import socket
import json
import threading


class NetworkServer:
    def __init__(self, port=5001, message_queue=None):
        self.port = port
        self.message_queue = message_queue

    def start(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', self.port))
                s.listen(5)
                print(f"[SERVER] Listening on port {self.port}")

                while True:
                    conn, addr = s.accept()
                    print(f"[SERVER] Connection from {addr}")
                    threading.Thread(
                        target=self.handle_client,
                        args=(conn,),
                        daemon=True
                    ).start()
        except Exception as e:
            print(f"[SERVER ERROR] {e}")

    def handle_client(self, conn):
        try:
            data = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
                if b"\n" in chunk:
                    break

            message = json.loads(data.decode('utf-8'))
            print(f"[SERVER] Received: {message}")

            if self.message_queue:
                self.message_queue.put(("sensor_data", message))

            conn.sendall(b"ACK\n")
        except Exception as e:
            print(f"[SERVER] Client error: {e}")
            if self.message_queue:
                self.message_queue.put(("error", str(e)))
        finally:
            conn.close()