import threading
from network import BlockchainServer, BlockchainClient

# Start the server in a separate thread


def start_server():
    server = BlockchainServer(5000)
    server.start_server()


server_thread = threading.Thread(target=start_server)
server_thread.start()

# Connect multiple clients to the server
clients = []
for i in range(3):  # Example with 3 clients
    client = BlockchainClient('127.0.0.1', 5000)
    client.connect_to_server()
    clients.append(client)

# Test sending data from clients
for client in clients:
    test_data = f"Test data from client {clients.index(client)}"
    client.send_data(test_data)

print("All tests executed. Check server output for data reception and client connection logs.")
