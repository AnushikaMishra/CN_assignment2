import socket
import os
import time

# Configuration
server_port = 12345
received_file = "received_file.txt"
enable_delayed_ack = False  # Change to True to enable Delayed-ACK

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configure Delayed-ACK
    if not enable_delayed_ack:
        server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)  # Disable Delayed-ACK
    else:
        server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 0)  # Enable Delayed-ACK

    server_socket.bind(('0.0.0.0', server_port))
    server_socket.listen(1)
    print("Server started. Waiting for client...")

    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    start_time = time.time()
    with open(received_file, 'wb') as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)

    conn.close()
    end_time = time.time()
    
    file_size = os.path.getsize(received_file)
    transfer_time = end_time - start_time
    throughput = file_size / transfer_time if transfer_time > 0 else 0

    print("\nServer Summary")
    print(f"File Received: {received_file}")
    print(f"File Size: {file_size} bytes")
    print(f"Transfer Time: {transfer_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} bytes/sec")
    print(f"Delayed-ACK: {'Enabled' if enable_delayed_ack else 'Disabled'}")
    print("Server task completed!")

if __name__ == '__main__':
    start_server()
