#!/usr/bin/env python
import socket
import threading
import sys


def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            print("An error occurred!")
            print(e)
            client.close()
            break


def send():
    username = input("Enter your username: ")
    client.send(username.encode('utf-8'))
    while True:
        message = input('')
        client.send(message.encode('utf-8'))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./client.py <IP> <PORT>")
        exit()

    HOST = str(sys.argv[1])
    PORT = int(sys.argv[2])

    if PORT < 0 or PORT > 65535 or not isinstance(PORT, int):
        print("Port number must be between 0 and 65535")
        exit()

    client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    send_thread = threading.Thread(target=send)
    send_thread.start()
