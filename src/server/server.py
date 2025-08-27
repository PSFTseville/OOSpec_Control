import os
import sys
import psutil
import numpy as np
import time
import matplotlib.pyplot as plt
import json
import socket


from src.com.spec import OceanHR
from src.server.commands import execute_command, decompose_command

class OHRServer(socket.socket):

    def __init__(self, PORT=12345, **kwargs):
        self.PORT = PORT
#        this_ip = os.popen("hostname -I").read().split()[0]
        hostname = socket.gethostname()
        this_ip = socket.gethostbyname(hostname)
        self.HOST = this_ip

        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((self.HOST, self.PORT))
        self.listen(5)

        print(f"Listening for commands on {self.HOST}:{self.PORT}")
        OHR = OceanHR(**kwargs)
        

    
    def run(self, **kwargs):

        while True:
            client_socket, client_address = self.accept()
            print(f'Connection stablished with {client_address}')

            OHR = OceanHR(**kwargs)

            while True:

                command = client_socket.recv(1028).decode().strip()

                if not command:
                    print(f'Client {client_address} disconnected')
                    break

                command = decompose_command(command)

                execute_command(command, OHR)



