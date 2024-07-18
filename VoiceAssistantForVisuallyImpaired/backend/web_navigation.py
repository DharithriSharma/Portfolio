#web navigation
import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib import robotparser
from googlesearch import search
import webbrowser
import threading
from youtubesearchpython import VideosSearch
from text_to_speech import speak
from speech_to_text import speech_to_text
import queue
import datetime
from summarization import summarize_text

# Global variables
is_reading = False
should_continue = True
reading_thread = None
searched_urls = []
command_queue = queue.Queue()

# Create a lock for synchronization
search_lock = threading.Lock()

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
    global is_reading, should_continue
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]

    def listen_for_commands():
        while should_continue:
            command = speech_to_text()
            if command:
                command_queue.put(command.lower())
            time.sleep(0.5)

    listening_thread = threading.Thread(target=listen_for_commands)
    listening_thread.start()

    content = ""  # Store the full content for summarization
    for chunk in chunks:
        if not should_continue:
            break
        print("Reading chunk:", chunk[:50])  # Debugging statement
        speak(chunk)
        content += chunk  # Append the chunk to the full content
        time.sleep(0.5)  # Pause slightly between chunks
        
        # Check for commands
        while not command_queue.empty():
            command = command_queue.get()
            if 'stop' in command:
                should_continue = False
                speak("Reading has been stopped.")
                break
            elif 'continue' in command:
                should_continue = True
                speak("Continuing the reading.")
            elif 'google' in command:
                searchGoogle(command.replace('google', '').strip())
            elif 'youtube' in command:
                searchYouTube(command.replace('youtube', '').strip())
            elif 'the time' in command:
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                speak(f"Sir, the time is {strTime}")

    listening_thread.join()
    is_reading = False
    should_continue = True

    # Automatic summarization after reading is complete
    if should_continue:
        speak("Now summarizing the content.")
        summary = summarize_text(content)
        speak(f"Here's a summary of the content: {summary}")

def searchGoogle(query):
    global is_reading, should_continue, reading_thread, searched_urls

    # Acquire the lock before performing the search
    search_lock.acquire()
    try:
        speak('Searching Google...')
        results = search(query)  # Get top 5 results to try
        for result in results:
            print(f"Processing result: {result}")
            if is_scraping_allowed(result):  # Check for scraping permission first
                speak(f"Opening the link: {result}")
                webbrowser.open(result)
                searched_urls.append(result)  # Add the URL to searched_urls list

                page = requests.get(result)
                soup = BeautifulSoup(page.content, 'html.parser')
                paragraphs = soup.find_all('p')
                scraped_text = ''
                for para in paragraphs:
                    scraped_text += para.get_text() + ' '

                is_reading = True
                should_continue = True
                reading_thread = threading.Thread(target=readContent, args=(scraped_text,))
                reading_thread.start()
                reading_thread.join()  # Wait for the reading to complete

                if not should_continue:
                    break
            else:
                speak("Sorry, scraping is not allowed on this website.")
                continue  # Move on to the next iteration of the loop
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

