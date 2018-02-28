import socket
import threading


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

    # Using an IP as the key, returns the nickname on join
    def get_nick(self, ip):
        return self.nicknames.get(ip, "Guest")

    # Adds a name to the dict
    def add_name(self, ip, name):
        self.nicknames[ip] = name

    # Listen to all connections - handling commands, printing data to console, printing any recieved data to console
    def listen(self, data, address):
        decoded = data.decode('utf-8')
        host_name = str(address[0]).replace("'", "")
        if decoded.startswith("PRIVMSG"):
            formatted_message = f"[{self.get_nick(address)}] {decoded[8:]}"
            self.send_message_all(formatted_message)
            print(formatted_message)
        elif decoded.startswith("NICK"):
            self.add_name(address, decoded[5:])
            on_join = f">> {self.get_nick(address)} has joined the server"
            self.send_message_all(on_join)
            print(f"{host_name} has changed nickname to {self.get_nick(address)}")
        else:
            print("Unsupported client! Please use Chatterclient.")

    # Sends message to all clients in connections[]
    def send_message_all(self, message):
        for i in self.connections:
            i.send(bytes(message, 'utf-8'))

    # Runs cleanup, displaying a person has left
    def disconnect(self, client_connection, client_address):
        self.connections.remove(client_connection)  # Removes connection socket from connection list
        client_connection.close()  # Closes the connection socket
        print("{} left".format(str(client_address)))
        host_name = self.get_nick(client_address)
        message_left_server = '{} has left the server'.format(host_name)
        self.send_message_all(message_left_server)

    # Thread handler
    def handler(self, client_connection, client_address):
        try:
            while True:
                data_info = client_connection.recv(1024)
                self.listen(data_info, client_address)
                if not data_info:
                    self.disconnect(client_connection, client_address)
                    break
        except ConnectionResetError:
            pass
        finally:
            self.disconnect(client_connection, client_address)

    # Executes server, runs a thread every time for each socket
    def execute(self):
        while True:
            client_connection, client_address = self.sock.accept()
            connection_thread = threading.Thread(target=self.handler, args=(client_connection, client_address))
            connection_thread.daemon = True  # Allows the thread to be closed, even if not completed
            connection_thread.start()
            self.connections.append(client_connection)
            self.nicknames[client_address] = None  # Place holder
            print("Incoming connection from " + str(client_address))


print("Chatterbox | Server | Server running IPv4, Protocol TCP")
try:
    server = Server(str(input("IP: ")), int(input("Port: ")))
    server.execute()
except ValueError or TypeError:
    print("Incorrect values entered. Server hostname must be in format x.x.x.x, server port must be in format 00000.")
except socket.error:
    print("Ensure your port/address is valid.")
