import os
import time
import threading
from gtts import gTTS
import pygame

pygame.mixer.init()

_tts_lock = threading.Lock()
_is_speaking = False
_stop_requested = False


def is_speaking():
    return _is_speaking


def stop_speaking():
    global _stop_requested, _is_speaking
    _stop_requested = True
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except:
        pass
    _is_speaking = False
    print("[TTS] Stopped speaking")


def speak(text):
    global _is_speaking, _stop_requested

    with _tts_lock:
        try:
            _stop_requested = False
            _is_speaking = True

            print(f"[TTS] Speaking: {text}")

            filename = "temp_tts.mp3"

            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

            tts = gTTS(text=text, lang="en")
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if _stop_requested:
                    break
                time.sleep(0.1)

            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except:
                pass

        except Exception as e:
            print("[TTS ERROR]", e)

        finally:
            _is_speaking = False
            _stop_requested = False