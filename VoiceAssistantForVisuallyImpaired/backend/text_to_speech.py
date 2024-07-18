#text-to-speech
import pyttsx3
import threading

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Create a lock for synchronization
lock = threading.Lock()

def speak(audio):
    # Acquire the lock before speaking
    lock.acquire()
    try:
        engine.say(audio)
        engine.runAndWait()
    finally:
        # Release the lock after speaking
        lock.release()

