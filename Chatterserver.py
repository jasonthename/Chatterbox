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

    # Send msg to all connections in list - two parameters, a Socket object (socket.accept(c, a) and the data to be sent
    def send_to_all(self, d, a):
        # Loops through all connections (socket that can send/recv data)
        for i in self.connections:
            host_name = str(a[0]).replace("'", "")  # IP Address w/o List format
            i.send(bytes(d))  # Send to all connections the received input
            received = d.decode('utf-8')  # Decodes parameter d - received input
            print(f'{[host_name]}: {received}')  # Prints all the received input in [IP]: Message format

    def disconnect(self, client_connection, client_address):
        host_name = str(client_address[0]).replace("'", "")  # IP Address w/o List format
        message_left_server = '{} has left the server'.format(host_name)  # A string that holds the default left message
        self.connections.remove(client_connection)  # Removes connection socket from connection list
        client_connection.close()  # Closes the connection socket
        self.send_to_all(bytes(message_left_server, 'utf-8'))  # send_to_all, someone left

    def handler(self, client_connection, client_address):
        try:
            while True:
                data_info = client_connection.recv(1024)  # Receive a maximum of 1024 bytes of data a thread
                self.send_to_all(data_info, client_address)
                if not data_info:
                    self.disconnect(client_connection, client_address)
        except ConnectionResetError:
            self.disconnect(client_connection, client_address)

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
            message_join_server = "{} has joined the server!".format(address)
            self.send_to_all(client_connection, bytes(message_join_server, 'utf-8'))


print("Chatterserver | Version 0.1 | Server running IPv4, Protocol TCP")
try:
    server = Server(str(input("IP: ")), int(input("Port: ")))
    server.execute()
except ValueError or TypeError:
    print("Incorrect values entered. Server hostname must be in format x.x.x.x, server port must be in format 00000.")
    print("")
except socket.error:
    print("Ensure your port/address is valid.")
