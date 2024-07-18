#main231.py
from speech_to_text import speech_to_text, wishMe
from web_navigation import searchGoogle, searchYouTube, summarize_text
from text_to_speech import speak
from my_transformers_script import answer_question
import datetime
from maill import send_email

def handleCommand(query):
    print(f"Handling command: {query}")  # Debug log
    if 'google' in query:
        query = query.replace("google", "")
        return searchGoogle(query)
    elif 'youtube' in query:
        query = query.replace("youtube", "")
        return searchYouTube(query)
    elif 'summarize' in query:
        return summarize_text(query)
    elif 'answering the question' in query:
        return answer_question(query, query)
    elif 'time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"Sir, the time is {strTime}")
        return strTime
    elif 'email' in query:
        send_email()
        return "Email function executed."
    else:
        return "Command not recognized."

def main():
    wishMe()
    query = speech_to_text()
    print(f"User query: {query}")  # Debug log
    if query:
        response = handleCommand(query.lower())
        print(f"Response: {response}")  # Debug log
        if response:
            speak(response)
        return response
    else:
        return "No command received."

if __name__ == "__main__":
    main()
