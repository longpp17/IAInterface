import sounddevice as sd

print(sd.query_devices())
sd.default.device = 1


def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    # Send audio data as bytes
    print(indata.tobytes())


with sd.InputStream(channels=1, device=1, callback=audio_callback):
    sd.sleep(10000)
    print('Press any key to stop')