# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import threading
import pyttsx3
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
# from googlesearch import search
from youtubesearchpython import VideosSearch
from web_navigation import searchGoogle, searchYouTube, summarize_text
from transformers import pipeline, TFBartForConditionalGeneration, AutoTokenizer
import time
from urllib import robotparser
import webbrowser

app = Flask(__name__)
CORS(app)

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Lock for synchronization
lock = threading.Lock()
search_lock = threading.Lock()

is_reading = False
should_continue = True
reading_thread = None
searched_urls = []

def speak(audio):
    print(f"Speaking: {audio}")
    lock.acquire()
    try:
        engine.say(audio)
        engine.runAndWait()
    finally:
        lock.release()

def is_scraping_allowed(url):
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    try:
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        user_agent = "*"  # Assuming we don't have a specific user agent
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        print(f"Error accessing robots.txt: {e}")
        return False

def readContent(text):
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    content = ""  # Store the full content for summarization
    for chunk in chunks:
        print(f"Reading chunk: {chunk[:50]}")  # Debugging statement
        speak(chunk)
        content += chunk  # Append the chunk to the full content
        time.sleep(0.5)  # Pause slightly between chunks
    return content

# def searchGoogle(query):
    global is_reading, should_continue, reading_thread, searched_urls

    # Acquire the lock before performing the search
    search_lock.acquire()
    try:
        speak('Searching Google...')
        # results = search(query)  # Get top 5 results to try
        query = query.replace("google", "")
        return searchGoogle(query)
        # for result in results:
        #     print(f"Processing result: {result}")
        #     if is_scraping_allowed(result):  # Check for scraping permission first
        #         speak(f"Opening the link: {result}")
        #         webbrowser.open(result)
        #         searched_urls.append(result)  # Add the URL to searched_urls list

        #         page = requests.get(result)
        #         soup = BeautifulSoup(page.content, 'html.parser')
        #         paragraphs = soup.find_all('p')
        #         scraped_text = ''
        #         for para in paragraphs:
        #             scraped_text += para.get_text() + ' '

        #         is_reading = True
        #         should_continue = True
        #         reading_thread = threading.Thread(target=readContent, args=(scraped_text,))
        #         reading_thread.start()
        #         reading_thread.join()  # Wait for the reading to complete

        #         if not should_continue:
        #             break
            # else:
                # speak("Sorry, scraping is not allowed on this website.")
                # continue  # Move on to the next iteration of the loop
    except:
        print("something went wrong")
    finally:
        # Release the lock after completing the search
        search_lock.release()

def searchYouTube(query):
    speak('Searching YouTube...')
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()
    if results['result']:
        video_url = results['result'][0]['link']
        speak(f"Here is what I found on YouTube")
        webbrowser.open(video_url)
    else:
        speak("Sorry, I couldn't find any videos on YouTube.")

# Create a pipeline for question answering
qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

def answer_question(query, context):
    print(f"Answering question: {query}")
    result = qa_pipeline(question=query, context=context)
    return result['answer']

def summarize_text(text, max_length=512):
    """Summarizes text using BART model with truncation."""
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
    model = TFBartForConditionalGeneration.from_pretrained("facebook/bart-base")

    truncated_text = text[:max_length]  # Truncate if text exceeds max_length

    inputs = tokenizer([truncated_text], return_tensors='tf')
    outputs = model.generate(**inputs)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary[:200]  # Limit summary length to 200 characters

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
    # elif 'email' in query:
    #     send_email()
    #     return "Email function executed."
    # else:
    #     return "Command not recognized."

@app.route('/voice-command', methods=['POST'])
def voice_command():
    data = request.get_json()
    command = data.get('command')
    if command:
        response = handleCommand(command.lower())
        print("this is response : ",response)
        return jsonify({'response': response})
    return jsonify({'response': 'No command received.'})

if __name__ == '__main__':
    app.run(debug=True)
