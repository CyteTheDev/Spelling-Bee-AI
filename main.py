# This code is made by Cyte
# WARNING.. THIS CAN GET YOU BANNED, YOU CAN CHANGE THE DELAY ON LINE 19.

import sounddevice as sd
import queue
import vosk
import json
import sys
import time
from pynput.keyboard import Controller, Key
GREEN = "\033[92m"
RESET = "\033[0m"
q = queue.Queue()
shared_model = None
TYPING_DELAY = 0.090 # Pretty fast, but yeah.

keyboard = Controller()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def load_model_once(path="model"):
    global shared_model
    if shared_model is None:
        shared_model = vosk.Model(path)
    return shared_model

def find_device_index(name_part):
    for i, d in enumerate(sd.query_devices()):
        if name_part.lower() in d['name'].lower() and d['max_input_channels'] > 0:
            return i
    raise ValueError(f"[-] Device with name containing '{name_part}' not found.")

def type_word(word):
    for c in word:
        keyboard.press(c)
        keyboard.release(c)
        time.sleep(0.01)
    time.sleep(0.05)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

def main():
    model = load_model_once("model")
    device_name = "CABLE Output"
    samplerate = 16000

    device_index = find_device_index(device_name)
    rec = vosk.KaldiRecognizer(model, samplerate)

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device_index,
                           dtype='int16', channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    last_word = text.split()[-1]
                    print(f"{GREEN}[+] detected word: [{last_word}]{RESET}")
                    type_word(last_word)
                    time.sleep(TYPING_DELAY)

if __name__ == "__main__":
    main()
