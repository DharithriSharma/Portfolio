import React, { useState, useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import './VoiceAssistant.css'; // Import CSS for styling

const VoiceAssistant = () => {
  const [response, setResponse] = useState('');
  const { transcript, resetTranscript } = useSpeechRecognition();

  const handleVoiceCommand = async () => {
    try {
      const res = await fetch('http://localhost:5000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: transcript }),
      });

      const data = await res.json();
      console.log("this is client data: ", data);
      setResponse(data.response);
      console.log(data.response);
      resetTranscript();
    } catch (error) {
      console.error("Error handling voice command", error);
    }
  };

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => console.log('Speech synthesis finished.');
    window.speechSynthesis.speak(utterance);
  };

  const handleStart = () => {
    speak("I AM YOUR VOICE ASSISTANT");
  };

  useEffect(() => {
    window.addEventListener('click', handleStart, { once: true });

    return () => {
      window.removeEventListener('click', handleStart);
    };
  }, []);

  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return <div>Your browser does not support speech recognition.</div>;
  }

  return (
    <div className="voice-assistant-container"> {/* Apply centering and background color styles */}
      <h1>I AM YOUR VOICE ASSISTANT</h1>
      <button 
        className="assistant-button"
        onClick={SpeechRecognition.startListening}
        onMouseEnter={() => speak('Start Listening')}
      >
        Start Listening
      </button>
      <button 
        className="assistant-button"
        onClick={handleVoiceCommand}
        onMouseEnter={() => speak('Submit Command')}
      >
        Submit Command
      </button>
      <button 
        className="assistant-button"
        onClick={SpeechRecognition.stopListening}
        onMouseEnter={() => speak('Stop Listening')}
      >
        Stop Listening
      </button>
      <p>Transcript: {transcript}</p>
      <p>Response: {response}</p>
    </div>
  );
};

export default VoiceAssistant;
