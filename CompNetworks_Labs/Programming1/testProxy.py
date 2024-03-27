import socket, threading

def handle_client(client_socket):
    # Read the client's request
    request = client_socket.recv(4096)

    # Forward the request to the remote server
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect(('www.example.com', 80))
    remote_socket.send(request)

    # Read the server's response
    response = remote_socket.recv(4096)

    # Forward the response back to the client
    client_socket.send(response)

    # Close the sockets
    remote_socket.close()
    client_socket.close()

def main():
    # Create a server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(5)

    # Wait for incoming client connections
    while True:
        client_socket, client_address = server_socket.accept()

        # Handle the client's request in a new thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
