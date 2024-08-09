# tcp_client.py

import socket
from utils import log, read_file, file_exists, get_file_size
from config import SERVER_IP, SERVER_PORT, FILE_PATH, CHUNK_SIZE

def main():
    # Check if the file exists
    if not file_exists(FILE_PATH):
        log(f"File {FILE_PATH} does not exist.")
        return

    # Set up the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    log(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

    # Send file data
    log(f"Sending file {FILE_PATH}...")
    total_size = get_file_size(FILE_PATH)
    total_sent = 0
    for chunk in read_file(FILE_PATH, CHUNK_SIZE):
        client_socket.sendall(chunk)
        total_sent += len(chunk)
        log(f"Sent chunk of size {len(chunk)} bytes. Total sent: {total_sent}/{total_size} bytes.")

    log("File sent successfully.")

    # Clean up
    client_socket.close()
    log("Client socket closed.")

if __name__ == "__main__":
    main()
