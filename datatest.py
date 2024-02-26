import pyaudio
import numpy as np

# Setup PyAudio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Initialize PyAudio
p = pyaudio.PyAudio()
device_index = 6
# Open stream
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=device_index)

# Read and print a few chunks of data
for _ in range(5):  # Read 5 chunks
    data = stream.read(CHUNK)
    np_data = np.frombuffer(data, dtype=np.int16)
    print(np_data)

# Stop and close the stream and terminate PyAudio
stream.stop_stream()
stream.close()
p.terminate()
