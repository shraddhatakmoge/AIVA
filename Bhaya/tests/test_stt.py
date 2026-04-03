from core.speech_to_text import transcribe

print("Speak something...")
text = transcribe()
print("You said:", text)