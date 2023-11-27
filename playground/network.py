import socket
import threading
import pickle


class BlockchainServer:
    def __init__(self, port):
        self.host = '127.0.0.1'  # Localhost for demonstration
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_nodes = []

    def start_server(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()

        print(f"Server listening on port {self.port}")

        try:
          while True:
              client_socket, address = self.socket.accept()
              self.connected_nodes.append(client_socket)
              print(f"Connection from {address}")

              client_thread = threading.Thread(
                  target=self.handle_client, args=(client_socket,))
              client_thread.start()
        except KeyboardInterrupt:
            print("Shutting down server...")
            for client_socket in self.connected_nodes:
                client_socket.close()
            self.socket.close()
            print("Server shutdown completed.")

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    # Process received data here
                    pass
            except:
                break

        client_socket.close()


class BlockchainClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.socket.connect((self.server_host, self.server_port))
            print(
                f"Connected to server at {self.server_host}:{self.server_port}")
        except socket.error as e:
            print(f"Connection error: {e}")

    def send_data(self, data):
        serialized_data = pickle.dumps(data)
        self.socket.send(serialized_data)


if __name__ == "__main__":
  # Example usage
  server = BlockchainServer(5000)
  client = BlockchainClient('127.0.0.1', 5000)

  # These should be run in separate threads or processes
  server.start_server()
  client.connect_to_server()
