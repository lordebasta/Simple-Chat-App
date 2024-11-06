#!/usr/bin/env python
import socket
import sys
import threading
import queue
from datetime import datetime

import commands


def log_handler():
    while True:
        msg, username = log_queue.get()

        # should I pass also the time?
        current_datetime = datetime.now()
        current_time = current_datetime.strftime("%H:%M:%S")
        with open("server.log", "a") as f:
            f.write(f"[{current_time}] - {username}: {msg}\n")
        log_queue.task_done()


def clients_manager():
    while True:
        args = clients_queue.get()
        cmd = args[0]
        client, username = args[1]
        if cmd == "remove":
            if client in clients:
                clients.remove(client)
            if username in usernames:
                usernames.remove(username)
        if cmd == "append":
            clients.append(client)
            usernames.append(username)


def handle_client(client, username):
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            msg = data.decode('utf-8')
            log_queue.put((msg, username))
            if msg.startswith('/'):
                msg = msg.lower()
                commands.handle_command(client, msg[1:], clients, usernames)
            else:
                broadcast(f"{username}: {msg}")
            client.close()
        except Exception as e:
            print(f"Error : {e}")
            break

    clients_queue.put(("remove", (client, username)))


def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))


if __name__ == "__main__":
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

    log_queue = queue.Queue()
    log_thread = threading.Thread(target=log_handler)
    log_thread.daemon = True
    log_thread.start()
    del log_thread

    clients_queue = queue.Queue()
    clients_thread = threading.Thread(target=clients_manager)
    clients_thread.daemon = True
    clients_thread.start()
    del clients_thread

    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f'Server listening on {HOST}:{PORT}')

    try:
        while True:
            client, address = server.accept()
            client.send("Welcome!".encode('utf-8'))
            username = client.recv(1024).decode('utf-8')
            clients_queue.put(("append", (client, username)))

            broadcast(f"{username} joined!")
            print(f'User {username} connected from {address}\n', end="")

            client_handler = threading.Thread(
                target=handle_client,
                args=(client, username)
            )
            client_handler.daemon = True
            client_handler.start()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        server.close()
