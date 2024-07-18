from flask import Flask, request, jsonify
import datetime
import smtplib
from urllib import robotparser
import requests
from googlesearch import search
from youtubesearchpython import VideosSearch
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask_cors import CORS
import threading
import time
from transformers import TFBartForConditionalGeneration
from transformers import AutoTokenizer
import pyttsx3
import speech_recognition as sr
# import wikipediaapi
import webbrowser

app = Flask(__name__)
CORS(app)

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

is_reading = False
should_continue = True
reading_thread = None
searched_urls = []
speak_lock = threading.Lock()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

def speak(audio):
    with speak_lock:
        engine.say(audio)
        engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am your voice assistant. Please tell me how may I help you")

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('t44321928@gmail.com', 'Test123@$')
    server.sendmail('youremail@gmail.com', to, content)
    server.close()

def is_scraping_allowed(url):
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    try:
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        user_agent = "*"  
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        print(f"Error accessing robots.txt: {e}")
        return False

def readContent(text):
    global is_reading, should_continue
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    for chunk in chunks:
        if not should_continue:
            break
        speak(chunk)
        time.sleep(0.5)

    is_reading = False
    should_continue = True

def summarize_text(text, max_length=512):
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
    model = TFBartForConditionalGeneration.from_pretrained("facebook/bart-base")

    truncated_text = text[:max_length]

    inputs = tokenizer([truncated_text], return_tensors='tf')
    outputs = model.generate(**inputs)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary[:200]

@app.route('/query', methods=['POST'])
def handleCommand():
    global is_reading, should_continue, reading_thread, searched_urls
    data = request.get_json()
    query = data['command'].lower()

    response_text = ""

    if 'wikipedia' in query:
        query = query.replace("wikipedia", "")
        # Implement searchWikipedia function or any required logic
        response_text = "Wikipedia search functionality is not implemented yet."

    elif 'google' in query:
        query = query.replace("google", "")
        response_text = searchGoogle(query)

    elif 'youtube' in query:
        query = query.replace("youtube", "")
        response_text = searchYouTube(query)

    elif 'the time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        response_text = f"The time is {strTime}"
        speak(f"the time is {strTime}")

    elif 'summarise' in query:
        if len(searched_urls) > 0:
            latest_url = searched_urls[-1]
            page = requests.get(latest_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            paragraphs = soup.find_all('p')
            scraped_text = ''
            for para in paragraphs:
                scraped_text += para.get_text() + ' '
            summary = summarize_text(scraped_text)
            response_text = f"Here's a summary of the previous search: {summary}"

    elif 'send an email' in query:
        try:
            response_text = "What is the recipient's email address?"
            to = takeCommand()
            response_text = "What should I say?"
            content = takeCommand()
            sendEmail(to, content)
            response_text = "Email has been sent!"
        except Exception as e:
            print(e)
            response_text = "Sorry, I am not able to send this email"

    elif 'stop' in query:
        if is_reading:
            should_continue = False
            is_reading = False
            if reading_thread and reading_thread.is_alive():
                reading_thread.join(timeout=0.5)
            response_text = "Reading has been stopped."

    elif 'continue' in query:
        if not is_reading and reading_thread:
            should_continue = True
            response_text = "Continuing the reading."
            reading_thread.start()

    is_reading = False
    should_continue = True

    return jsonify({"response": response_text})

def searchGoogle(query):
    global is_reading, should_continue, reading_thread, searched_urls

    #speak('Searching Google...')
    results = search(query)  # Get top 5 results to try
    for result in results:
        print(f"Processing result: {result}")
        if is_scraping_allowed(result):  # Check for scraping permission first
            print(f"Opening the link: {result}")
            webbrowser.open(result)
            #open_browser(result)
            searched_urls.append(result)  # Add the URL to searched_urls list

            page = requests.get(result)
            soup = BeautifulSoup(page.content, 'html.parser')
            paragraphs = soup.find_all('p')
            scraped_text = ''
            for para in paragraphs:
                scraped_text += para.get_text() + ' '

            is_reading = True  # For potential future reading functionality (optional)
            should_continue = True
            reading_thread = threading.Thread(target=readContent, args=(scraped_text,))
            reading_thread.start()
            reading_thread.join()  # Wait for the reading to complete

            if not should_continue:
                break
        else:
            speak("Sorry, scraping is not allowed on this website.")
            continue  # Move on to the next iteration of the loop
def searchYouTube(query):
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()
    if results['result']:
        video_url = results['result'][0]['link']
        webbrowser.open(video_url)
        speak(f"Here is what I found on YouTube")
    else:
        speak("Sorry, I couldn't find any videos on YouTube.")
    
# def open_browser(url):
#     print(f"Attempting to open browser for URL: {url}")
#     success = webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible
#     if success:
#         speak(f"Successfully opened {url} in web browser.")
#     else:
#         print(f"Failed to open {url} in web browser.")
#     time.sleep(1)  # Give a little time for the browser to open

if __name__ == "__main__":
    app.run(debug=True)
