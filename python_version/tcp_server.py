# tcp_server.py

import socket
from utils import log, write_file
from config import SERVER_IP, SERVER_PORT, FILE_PATH, CHUNK_SIZE

def main():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)
    log(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    # Wait for a connection from the client
    conn, addr = server_socket.accept()
    log(f"Connection established with {addr}")

    # Receive file data
    log("Receiving file data...")
    data = bytearray()
    while True:
        chunk = conn.recv(CHUNK_SIZE)
        if not chunk:
            break
        data.extend(chunk)
        log(f"Received chunk of size {len(chunk)} bytes.")

    # Write the received data to a file
    if data:
        write_file(FILE_PATH, data)
        log(f"File received successfully and saved to {FILE_PATH}.")

    # Clean up
    conn.close()
    server_socket.close()
    log("Server socket closed.")

if __name__ == "__main__":
    main()
