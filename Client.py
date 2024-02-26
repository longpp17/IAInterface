import socket
import pyaudio
import threading

# Setup audio stream
FORMAT = pyaudio.paInt16
CHANNELS =  1
RATE =  44100
CHUNK =  1024


server_ip = input("Enter the server's IP address: ")
port = int(input("Enter the server's port: "))
# Create a socket to connect to the server
s = socket()
s.connect((server_ip, port))  # Replace <SERVER_IP> with the server's IP address

print("Connected to the server")
print("press Ctrl+C to stop the audio stream")

# Function to play received audio data
def play_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    while True:
        data = s.recv(CHUNK)
        print("data received")
        print(data)

        stream.write(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()

play_audio()

# Start playing audio in a separate thread
# threading.Thread(target=play_audio).start()
