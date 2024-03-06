import time

import pyaudio
import asyncio
import socketio
from aioconsole import ainput

# Initialize PyAudio and socket.io async client
p = pyaudio.PyAudio()
sio = socketio.AsyncClient(logger=True, engineio_logger=True)

# Constants for audio stream configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
stream = None

stream_microphone = True

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
    if stream_microphone:
        while True:
            data = local_stream.read(CHUNK, exception_on_overflow=False)
            await sio.emit('audio-buffer', data)
            await asyncio.sleep(0)


@sio.on('audio-buffer')
async def on_audio(data):
    print("Received audio buffer from the server: ", data)
    if stream is not None:
        stream.write(data)


async def main():
    input_devices, output_devices = await get_device_index(p)

    print("Available input devices: ")
    print(input_devices)
    input_device_index = int(await ainput("Enter the index of the device you want to use, type -1 to listen only: "))
    if input_device_index == -1:
        global stream_microphone
        stream_microphone = False
        input_device_index = 0


    print("Available output devices: ")
    print(output_devices)
    output_device_index = int(await ainput("Enter the index of the device you want to use: "))

    await sio.connect('http://localhost:3000')
    print('Connected to the server with SID:', sio.sid)

    print("Entering Bootstrap Link, Input 'done' to complete")
    links = []
    while True:
        link = await ainput("Enter the bootstrap link: ")
        if link == 'done':
            break
        else:
            links.append(link)
    await sio.emit('setup-bootstrap', links)
    print("setup-bootstrap event emitted with data:", links)


    global stream
    stream = await get_stream(p, input_device_index, output_device_index)
    await broadcast(stream)


if __name__ == '__main__':
    asyncio.run(main())


