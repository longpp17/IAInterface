# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import pyaudio
import socket
from srudp import SecureReliableSocket
import threading
# Create an instance of PyAudio
p = pyaudio.PyAudio()


def get_device_index(p: pyaudio.PyAudio):
    # return: [index: device_name]
    devices = p.get_device_count()
    device_index = {}
    for i in range(devices):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:
            device_index[i] = device_info.get('name')
    return device_index

def get_stream(p: pyaudio.PyAudio, device_index: int):
    # Open a stream with the device index
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=device_index)
    return stream


def broadcast(stream: pyaudio.Stream, clients: list):
    # Broadcast the stream to all clients

    while True:
        data = stream.read(1024)
        for client in clients:
            client.sendall(data)

def setup_server(port: int):
    # Create a socket server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    return server


def handle_stream(stream: pyaudio.Stream, current_client: socket,clients_list: list):
    while True:
        try:
            broadcast(stream, clients_list)
        except:
            clients_list.remove(current_client)
            current_client.close()
            break


def main():
    device_index = get_device_index(p)

    print("Available devices: ")
    print(device_index)
    device_index = int(input("Enter the index of the device you want to use: "))
    stream = get_stream(p, device_index)
    clients = []

    port = int(input("Enter the port to run the server on: "))
    server = setup_server(port)
    print("Server running")
    while True:
        client, addr = server.accept()
        clients.append(client)
        print(f"Connected with {addr}")
        stream = get_stream(p, device_index)
        client_thread = threading.Thread(target=handle_stream, args=(stream, client, clients))
        client_thread.start()

main()