import socket
import threading
import urllib.request
import random


# Someones external service that returns external IP without the use of a library
external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

print(external_ip)


class Server:

    # Passing two parameters to a socket method - 1st - IPV4 Connection, and 2nd - TCP protocol (SOCK_STREAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # A list of connections
    connections = []

    # A list of nicknames
    nicknames = {}

    def __init__(self, host_ip, host_port):
        # Bind socket to an address and port
        self.sock.bind((host_ip, host_port))

        # Listen to a port, 5 is the recommended max
        self.sock.listen(1)

    def get_nick(self, ip):
        return self.nicknames.get(ip, "Guest")

    def add_name(self, ip, name):
        self.nicknames[ip] = name

    # Send msg to all connections in list - two parameters, a Socket object (socket.accept(c, a) and the data to be sent
    def send_to_all(self, d, a):
        # Loops through all connections (socket that can send/recv data)
        for i in self.connections:
            decoded = d.decode('utf-8')
            if decoded.startswith("PRIVMSG"):
                host_name = self.get_nick(a).replace("'", "")
                raw_msg = decoded[8:]
                message = f"[{host_name}] {raw_msg}".encode('utf-8')
                i.send(bytes(message))  # Send to all connections the received input
                print(message.decode('utf-8'))
            elif decoded.startswith("NICK"):
                name = decoded[5:]
                self.add_name(a, name)
                on_join = f">> {self.get_nick(a)} has joined the server".encode('utf-8')
                i.send(bytes(on_join))

    def disconnect(self, client_connection, client_address):
        host_name = str(client_address[0]).replace("'", "")  # IP Address w/o List format
        message_left_server = '{} has left the server'.format(host_name)  # A string that holds the default left message
        self.connections.remove(client_connection)  # Removes connection socket from connection list
        client_connection.close()  # Closes the connection socket
        self.send_to_all(bytes(message_left_server, 'utf-8'), client_address)  # send_to_all, someone left

    def handler(self, client_connection, client_address):
        try:
            while True:
                data_info = client_connection.recv(1024)  # Receive a maximum of 1024 bytes of data a thread
                self.send_to_all(bytes(data_info), client_address)  # Sends what is received to all connected
                if not data_info:  # If no data is received
                    self.disconnect(client_connection, client_address)  # Run disconnect cleanup
        except ConnectionResetError:  # If a ConnectionResetError is thrown
            pass  # Log ConnectionResetError
        finally:
            self.disconnect(client_connection, client_address)  # Run cleanup

    def execute(self):
        print("Listening for connections..")
        # Loop to handle connection
        while True:
            # Accepts the connection through the socket
            client_connection, client_address = self.sock.accept()
            # Creates a connection thread
            connection_thread = threading.Thread(target=self.handler, args=(client_connection, client_address))
            connection_thread.daemon = True  # Ensure we can close out of the thread if needed
            connection_thread.start()  # Runs the thread
            self.connections.append(client_connection)  # Adds to a list of connections
            self.nicknames[client_address] = ""
            print("Incoming connection from " + str(client_address))


print("Chatterserver | Version 0.1 | Server running IPv4, Protocol TCP")
try:
    server = Server(str(input("IP: ")), int(input("Port: ")))
    server.execute()
except ValueError or TypeError:
    print("Incorrect values entered. Server hostname must be in format x.x.x.x, server port must be in format 00000.")
except socket.error:
    print("Ensure your port/address is valid.")
