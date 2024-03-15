import time

import pyaudio
import asyncio
import socketio
from aioconsole import ainput
import os
from threading import Thread
# Initialize PyAudio and socket.io async client
p = pyaudio.PyAudio()
sio = socketio.AsyncClient()

# Constants for audio stream configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
stream = None

stream_microphone = True
# TODO: Save bootstrap server URL in a config file
broadcast_loop = None
INPUT_DEVICE_INDEX = None
OUTPUT_DEVICE_INDEX = None


# Function to run the asyncio event loop in a separate thread
def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()





# Function to schedule coroutines to run in the asyncio event loop thread
def run_coroutine_threadsafe(coro):
    new_loop = asyncio.new_event_loop()
    t = Thread(target=start_asyncio_loop, args=(new_loop,))
    t.start()  # Start the new thread, which starts the event loop
    return asyncio.run_coroutine_threadsafe(coro, new_loop)


async def get_device_index(p: pyaudio.PyAudio):
    devices = p.get_device_count()
    input_devices, output_devices = {}, {}

    for i in range(devices):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:
            input_devices[i] = device_info.get('name')
        if device_info.get('maxOutputChannels') > 0:
            output_devices[i] = device_info.get('name')
    return input_devices, output_devices


async def get_stream(p: pyaudio.PyAudio, input_device_index: int, output_device_index: int):
    if not stream_microphone:
        local_stream = p.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              output=True,
                              output_device_index=output_device_index,
                              frames_per_buffer=CHUNK)
    else:
        local_stream = p.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              output=True,
                              input_device_index=input_device_index,
                              output_device_index=output_device_index,
                              frames_per_buffer=CHUNK)
    return local_stream


async def broadcast(local_stream: pyaudio.Stream):
    # if stream_microphone:
    while True:
        data = local_stream.read(CHUNK, exception_on_overflow=False)

        await sio.emit('audio-buffer', data)
        await asyncio.sleep(0)


@sio.on("get-peers")
async def on_get_peers(data: str):
    print("Received list of peers: ", data)


@sio.on('audio-buffer')
async def on_audio(data):
    print("Received audio buffer from the server: ", data)
    if stream is not None:
        stream.write(data)


async def parse_user_input(user_input, p: pyaudio.PyAudio, sio: socketio.AsyncClient):
    commands = user_input.split(" ")

    if commands[0] == "help":
        print("Available commands: ")
        print("help: display this help message")
        print("exit: exit the program")
        print("display input/output/all-devices: display the available input and output devices")
        print("display peers: display the list of peers")
        print("switch input/output <index>: switch the input and output devices")
        print("switch i <index> o <index>: switch the input and output devices")
        print("stream on/off: turn on/off the audio stream")
        print("stream to <peer_id>: stream audio to a peer")

    elif commands[0] == "exit":
        print("Exiting the program...")
        exit(0)

    elif commands[0] == "display":
        input_devices, output_devices = await get_device_index(p)
        if commands[1] == "input":
            print("Available input devices: ")
            print(input_devices)
        elif commands[1] == "output":
            print("Available output devices: ")
            print(output_devices)
        elif commands[1] == "all-devices":
            print("Available input devices: ")
            print(input_devices)
            print("Available output devices: ")
            print(output_devices)
        elif commands[1] == "peers":
            await sio.emit("get-peers")
        else:
            print("Invalid command")

    elif commands[0] == "switch":
        global INPUT_DEVICE_INDEX, OUTPUT_DEVICE_INDEX
        if commands[1] == "input":
            INPUT_DEVICE_INDEX = int(commands[2])
            if INPUT_DEVICE_INDEX == -1:
                global stream_microphone
                stream_microphone = False
                print("Input device switched to: ", "Default")
            else:
                print("Input device switched to: ", INPUT_DEVICE_INDEX)
        elif commands[1] == "output":
            OUTPUT_DEVICE_INDEX = int(commands[2])
            print("Output device switched to: ", OUTPUT_DEVICE_INDEX)
        elif commands[1] == "i" and commands[3] == "o":
            INPUT_DEVICE_INDEX = int(commands[2])
            OUTPUT_DEVICE_INDEX = int(commands[4])
            print("Input device switched to: ", INPUT_DEVICE_INDEX)
            print("Output device switched to: ", OUTPUT_DEVICE_INDEX)
        else:
            print("Invalid command")

    elif commands[0] == "stream":
        if commands[1] == "on":
            global stream
            if INPUT_DEVICE_INDEX is None:
                print("Please select input device first")
                return

            if OUTPUT_DEVICE_INDEX is None:
                print("Please select output device first")
                return

            stream = await get_stream(p, INPUT_DEVICE_INDEX, OUTPUT_DEVICE_INDEX)
            print("Stream started")
            # await broadcast(stream)
            global broadcast_loop
            broadcast_loop = run_coroutine_threadsafe(broadcast(stream))

        elif commands[1] == "off":
            # guard insure stream and broadcast_loop are not None
            print("Stopping stream")
            if stream is None:
                print("Stream is already off")
                return
            if broadcast_loop is None:
                print ("Broadcast loop is already off")

            stream.stop_stream()
            stream.close()
            stream = None
            broadcast_loop.done()

        elif commands[1] == "to":
            peer_id = commands[2]
            if peer_id is not None:
                await sio.emit('stream-to-peer', peer_id)
            else:
                print("Invalid command")

        else:
            print("Invalid command")

    else:
        print("Invalid command")


async def handle_user_input(p: pyaudio.PyAudio, sio: socketio.AsyncClient):
    while True:
        user_input = await ainput("enter help for help:")
        await parse_user_input(user_input, p, sio)


async def create_bootstrap_links():
    print("Entering Bootstrap Link, Input 'done' to complete")
    links = []
    while True:
        link = await ainput("Enter the bootstrap link: ")
        if link == 'done':
            break
        else:
            links.append(link)
    await sio.emit('setup-bootstrap', links)

    with open("./bootstrap.txt", 'w') as f:
        for link in links:
            f.write(link + "\n")

    print("setup-bootstrap event emitted with data:", links)


async def setup_bootstrap_links(bootstrap_file="./bootstrap.txt"):
    if os.path.exists(bootstrap_file):
        with open(bootstrap_file, 'r') as f:
            links = f.readlines()
        await sio.emit('setup-bootstrap', links)
        print("setup-bootstrap event emitted with data:", links)
    else:
        print("No bootstrap file found")
        await create_bootstrap_links()


async def main():
    await sio.connect('http://localhost:3000')
    print('Connected to the server with SID:', sio.sid)

    await setup_bootstrap_links()
    await handle_user_input(p, sio)


if __name__ == '__main__':
    asyncio.run(main())
