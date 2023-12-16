import socket

def main():
    print("Welcome to the Music Player CLI. Type 'help' to see available commands.")
    host = "localhost"
    port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        while True:
            command = input(">> ")
            client_socket.sendall(command.encode())
            response = client_socket.recv(4096).decode()
            print(response)

if __name__ == '__main__':
    main()