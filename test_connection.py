import socket

# Connect to OceanHR server and send commands
HOST = '10.10.1.87'  # The server's hostname or IP address
PORT = 12345        # The port used by the server

OceanSocket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command = "MEAS"
OceanSocket.connect((HOST, PORT))
OceanSocket.sendall(command.encode())