'''
 # @ Author: Ahmad Shayaan
 # @ Create Time: 2023-08-21 14:55:07
 # @ Modified by: Ahmad Shayaan
 # @ Modified time: 2023-08-22 20:44:04
 # @ Description:
 '''

import socket
import json

HOST = "127.0.0.1"
PORT = 8893

def send_command(command, socket):
    socket.send(command.encode('utf-8'))
    response = socket.recv(1024).decode('utf-8')
    return json.loads(response)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    while True:
        command = input("Enter command: ")
        response = send_command(command, client_socket)
        print(response)
        if command == "END":
            break

if __name__ == "__main__":
    main()