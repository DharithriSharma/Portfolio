#speech to text
import speech_recognition as sr
import datetime
from text_to_speech import speak
import threading

def wishMe():
    speak("Hello,I am your voice assistant. Please tell me how may I help you")


# Create a lock for synchronization
# lock = threading.Lock()

# def wishMe():
#     hour = int(datetime.datetime.now().hour)
#     if hour >= 0 and hour < 12:
#         speak_with_lock("Good Morning!")
#     elif hour >= 12 and hour < 18:
#         speak_with_lock("Good Afternoon!")
#     else:
#         speak_with_lock("Good Evening!")
#     speak_with_lock("I am your voice assistant. Please tell me how may I help you")

# def speak_with_lock(message):
#     # Acquire the lock before speaking
#     lock.acquire()
#     try:
#         speak(message)
#     finally:
#         # Release the lock after speaking
#         lock.release()


def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return None
