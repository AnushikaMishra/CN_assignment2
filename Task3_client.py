import socket
import time
import os

# Configuration
server_ip = "127.0.0.1"  # Change if the server is on another machine
server_port = 12345
file_to_send = "file_to_send.txt"
enable_nagle = False  # Change to True to enable Nagle’s Algorithm

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configure Nagle’s Algorithm
    if not enable_nagle:
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle's Algorithm
    else:
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)  # Enable Nagle's Algorithm

    client_socket.connect((server_ip, server_port))
    print("Client connected to server, sending file...")

    start_time = time.time()
    file_size = os.path.getsize(file_to_send)

    with open(file_to_send, 'rb') as f:
        data = f.read(1024)
        while data:
            client_socket.send(data)
            data = f.read(1024)
            time.sleep(1/40)  # Simulate 40 bytes/sec transfer rate

    client_socket.close()
    end_time = time.time()

    transfer_time = end_time - start_time
    throughput = file_size / transfer_time if transfer_time > 0 else 0

    print("\nClient Summary")
    print(f"File Sent: {file_to_send}")
    print(f"File Size: {file_size} bytes")
    print(f"Transfer Time: {transfer_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} bytes/sec")
    print(f"Nagle’s Algorithm: {'Enabled' if enable_nagle else 'Disabled'}")
    print("Client task completed!")

if __name__ == '__main__':
    start_client()
