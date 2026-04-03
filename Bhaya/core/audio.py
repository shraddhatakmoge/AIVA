from pvrecorder import PvRecorder

recorder = None

def start_recorder():
    global recorder

    if recorder is None:
        recorder = PvRecorder(
            device_index=-1,   # default microphone
            frame_length=512
        )
        recorder.start()


def read_audio():
    if recorder is not None:
        return recorder.read()
    return None


def stop_recorder():
    global recorder

    if recorder is not None:
        recorder.stop()
        recorder.delete()
        recorder = None
        