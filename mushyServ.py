import socket
import threading


class Server:

    # Passing two parameters to a socket method - 1st - IPV4 Connection, and 2nd - TCP protocol (SOCK_STREAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # A list which would include all connections
    connections = []

    def __init__(self, host_ip, host_port):
        # Bind socket to an address and port
        self.sock.bind((host_ip, host_port))

        # Listen to a port, 5 is the recommended max
        self.sock.listen(1)

    def disconnect(self, client_connection):
        host_name = str(self.sock.getsockname()[0]).replace("'", "")
        print('{} has left the server'.format(host_name))
        self.connections.remove(client_connection)
        client_connection.close()

    def handler(self, client_connection, client_address):
        try:
            while True:
                data_info = client_connection.recv(1024)  # Receive a maximum of 1024 bytes of data a thread
                for i in self.connections:
                    host_name = str(self.sock.getsockname()[0]).replace("'", "")
                    i.send(bytes(data_info))  # Send to all connections the received input
                    received = data_info.decode('utf-8')
                    print(f'{[host_name]}: {received}')
                if not data_info:
                    self.disconnect(client_connection)
        except ConnectionResetError:
            self.disconnect(client_connection)

    def execute(self):
        # Loop to handle connection
        while True:
            # Accepts the connection through the socket
            client_connection, client_address = self.sock.accept()
            # Creates a connection thread
            connection_thread = threading.Thread(target=self.handler, args=(client_connection, client_address))
            connection_thread.daemon = True
            connection_thread.start()
            self.connections.append(client_connection)
            address = str(client_address[0])
            print('{} has joined the server'.format(address))


print("mushyServ | Version 0.1 | Server running IPv4, Protocol TCP")
try:
    server = Server('0.0.0.0', 10000)
    server.execute()
except ValueError:
    print("Incorrect values entered. Server hostname must be in format x.x.x.x, server port must be in format 00000.")
    print("")
except socket.error:
    print("Ensure your port/address is valid.")
