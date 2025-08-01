#!/usr/bin/env python3
"""
JARVIS Web Interface
Web-based AI Assistant with Iron Man-style UI
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import sys
import json
import requests
import wikipedia
import psutil
import subprocess
import threading
import time
from dotenv import load_dotenv
import base64
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

class WebJarvis:
    def __init__(self):
        """Initialize Web Jarvis"""
        load_dotenv()

        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'male' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()

        # System status
        self.is_active = True

    def speak(self, text):
        """Text to speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except:
            return False

    def process_command(self, command):
        """Process text commands"""
        command = command.lower().strip()

        try:
            # Time and date commands
            if any(word in command for word in ['time', 'what time']):
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                response = f"The time is {current_time}, Sir."

            elif any(word in command for word in ['date', 'what date', 'today']):
                current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
                response = f"Today is {current_date}, Sir."

            # System status
            elif any(word in command for word in ['system status', 'system info', 'computer status']):
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                response = f"System Status - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%"

            # Wikipedia search
            elif 'wikipedia' in command or 'wiki' in command:
                search_terms = command.replace('wikipedia', '').replace('wiki', '').strip()
                if search_terms:
                    try:
                        summary = wikipedia.summary(search_terms, sentences=2)
                        response = f"According to Wikipedia: {summary}"
                    except wikipedia.exceptions.DisambiguationError:
                        response = f"Multiple results found for {search_terms}. Please be more specific, Sir."
                    except wikipedia.exceptions.PageError:
                        response = f"No Wikipedia page found for {search_terms}, Sir."
                else:
                    response = "What would you like me to look up on Wikipedia, Sir?"

            # Math calculations
            elif any(word in command for word in ['calculate', 'math', 'compute']):
                import re
                math_expression = re.findall(r'[\d+\-*/\(\)\.\s]+', command)
                if math_expression:
                    expression = ''.join(math_expression).strip()
                    try:
                        result = eval(expression)
                        response = f"The result is {result}, Sir."
                    except:
                        response = "I couldn't calculate that expression, Sir."
                else:
                    response = "I didn't understand the mathematical expression, Sir."

            # Weather
            elif 'weather' in command:
                response = "I would need a weather API key to provide current weather information, Sir."

            # Default response
            else:
                responses = [
                    "I understand, Sir. How else may I assist you?",
                    "Interesting, Sir. What would you like me to do next?",
                    "At your service, Sir. How can I help?",
                    "I'm here to assist you, Sir. What do you need?"
                ]
                import random
                response = random.choice(responses)

            return response

        except Exception as e:
            return "I encountered an error processing that command, Sir."

# Initialize Jarvis instance
jarvis = WebJarvis()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def process_command_api():
    """Process text command via API"""
    data = request.get_json()
    command = data.get('command', '')

    if command:
        response = jarvis.process_command(command)

        # Optional: Speak the response
        if data.get('speak', False):
            threading.Thread(target=jarvis.speak, args=(response,)).start()

        return jsonify({
            'status': 'success',
            'response': response,
            'timestamp': datetime.datetime.now().isoformat()
        })

    return jsonify({
        'status': 'error',
        'response': 'No command provided'
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'message': 'Connected to Jarvis', 'status': 'online'})

@socketio.on('command')
def handle_command(data):
    """Handle real-time command via WebSocket"""
    command = data.get('command', '')

    if command:
        response = jarvis.process_command(command)

        emit('response', {
            'command': command,
            'response': response,
            'timestamp': datetime.datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("🤖 Starting Jarvis Web Interface...")
    print("🌐 Access Jarvis at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)