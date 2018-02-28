import socket
import threading


class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host_ip, host_port):
        self.sock.connect((host_ip, host_port))

        input_thread = threading.Thread(target=self.send_msg)
        input_thread.daemon = True
        input_thread.start()

        self.listen()

    def close(self):
        self.sock.close()
        self.sock.shutdown()

    def enter_name(self):
        name = input("What's your name? ")
        while len(name) >= 16:
            print("Woah, that's way too long!")
            name = input("What's your name? ")
        self.sock.send(bytes("NICK " + name, 'utf-8'))

    def send_msg(self):
        self.enter_name()
        while True:
            self.sock.send(bytes("PRIVMSG " + input("> "), 'utf-8'))

    def listen(self):
        print('Listening to {}'.format(str(self.sock.getsockname())))
        while True:
            response = self.sock.recv(1024)
            response_decoded = response.decode('utf-8')
            print("\n" + response_decoded)
            if not response:
                print("No information is being recevied..")
                break


try:
    print("Chatterbox | A Python-powered talking thing.")
    client = Client(str(input("IP: ")), int(input("Port: ")))
except socket.error:
    print("Could not connect to server.")
except ValueError or TypeError:
    print("Incorrect values entered. Server hostname must be in format x.x.x.x, server port must be in format 00000.")



