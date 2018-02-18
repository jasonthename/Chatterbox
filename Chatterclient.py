import socket
import threading


class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host_ip, host_port):
        print('Listening to {}:{}'.format(host_ip, host_port))
        self.sock.connect((host_ip, host_port))

        input_thread = threading.Thread(target=self.send_msg)
        input_thread.daemon = True
        input_thread.start()

        self.listen()

    def close(self):
        self.sock.close()
        self.sock.shutdown()

    def send_msg(self):
        while True:
            self.sock.send(bytes(input("\n> "), 'utf-8'))

    def listen(self):
        while True:
            response = self.sock.recv(1024)
            host_name = str(self.sock.getsockname()[0]).replace("'", "")
            response_decoded = response.decode('utf-8')
            print(f'[{host_name}]: {response_decoded}\n')
            if not response:
                print("No information is being recevied..")
                break


try:
    print("Chatterbox | Version 0.2")
    client = Client(str(input("IP: ")), int(input("Port: ")))
except socket.error:
    print("Could not connect to server.")
except ValueError or TypeError:
    print("Incorrect values entered. Server hostname must be in format x.x.x.x, server port must be in format 00000.")



