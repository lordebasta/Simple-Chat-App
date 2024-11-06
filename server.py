#!/usr/bin/python3
import socket
import sys
import threading
import commands
from datetime import datetime

if len(sys.argv) != 3:
    print("Usage: ./server.py <IP> <PORT>")
    exit()

HOST = str(sys.argv[1])
PORT = int(sys.argv[2])

if PORT < 0 or PORT > 65535 or not isinstance(PORT, int):
    print("Port number must be between 0 and 65535")
    exit()

clients = []
usernames = []

server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f'Server listening on {HOST}:{PORT}')


def handle_client(client, username):
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            msg = data.decode('utf-8')
            log(msg, username)
            if msg.startswith('/'):
                msg = msg.lower()
                commands.handle_command(client, msg[1:], clients, usernames)
            else:
                broadcast(f"{username}: {msg}")
            client.close()
        except Exception as e:
            print(f"Error : {e}")
            break
    remove(client, username)


def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))


def remove(client, username):
    if client in clients:
        clients.remove(client)
    if username in usernames:
        usernames.remove(username)


def log(message, username):
    current_datetime = datetime.now()
    current_time = current_datetime.strftime("%H:%M:%S")
    try:
        with open("server.log", "a") as f:
            f.write(f"[{current_time}] - {username}: {message}\n")
    except IOError as e:
        print(f"An error has occured during logging: {e}")


try:
    while True:
        client, address = server.accept()
        client.send("Welcome!".encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        clients.append(client)
        usernames.append(username)

        broadcast(f"{username} joined!")
        print(f'User {username} connected from {address}')

        client_handler = threading.Thread(
            target=handle_client,
            args=(client, username)
        )
        client_handler.start()
except KeyboardInterrupt:
    print("\nServer stopped.")
    server.close()
