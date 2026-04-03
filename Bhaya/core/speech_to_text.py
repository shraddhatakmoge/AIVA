import speech_recognition as sr


def transcribe(timeout=5, phrase_time_limit=7):
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("[STT] Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            print("[STT] Listening...")
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        print("[STT] Recognizing...")
        text = recognizer.recognize_google(audio)

        print("[STT] Recognized:", text)
        return text

    except sr.WaitTimeoutError:
        print("[STT ERROR] Listening timed out")
        return ""

    except sr.UnknownValueError:
        print("[STT ERROR] Could not understand audio")
        return ""

    except sr.RequestError as e:
        print("[STT ERROR] API error:", e)
        return ""

    except Exception as e:
        print("[STT ERROR] General error:", e)
        return ""