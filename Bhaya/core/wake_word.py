import pvporcupine
from config import ACCESS_KEY
from core.audio import read_audio

porcupine = None

def init_wake_word():
    global porcupine

    if porcupine is None:
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=["jarvis"]
        )


def detect_wake_word():
    while True:
        pcm = read_audio()

        if pcm is None:
            continue

        result = porcupine.process(pcm)

        if result >= 0:
            return True