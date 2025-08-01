#!/usr/bin/env python3
"""
JARVIS - Just A Rather Very Intelligent System
AI Assistant inspired by Tony Stark's Jarvis from Iron Man
"""

import speech_recognition as sr
import pyttsx3
import openai
import datetime
import webbrowser
import os
import sys
import json
import requests
import wikipedia
import psutil
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from colorama import init, Fore, Style
import threading
import time
from dotenv import load_dotenv

# Initialize colorama and rich
init(autoreset=True)
console = Console()

class JarvisAI:
    def __init__(self):
        """Initialize Jarvis AI Assistant"""
        load_dotenv()

        # Initialize speech recognition and text-to-speech
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()

        # Configure TTS voice
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to find a male voice for more Jarvis-like experience
            for voice in voices:
                if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break

        self.tts_engine.setProperty('rate', 180)  # Speaking rate
        self.tts_engine.setProperty('volume', 0.9)  # Volume level

        # OpenAI API setup (optional - can work without it)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

        # Jarvis personality and responses
        self.wake_words = ['jarvis', 'hey jarvis', 'hello jarvis']
        self.goodbye_words = ['goodbye', 'exit', 'quit', 'shutdown', 'sleep']

        # System status
        self.is_listening = False
        self.is_active = True

        self.display_startup()

    def display_startup(self):
        """Display Jarvis startup animation"""
        startup_text = Text("JARVIS", style="bold cyan")
        startup_text.append(" - Just A Rather Very Intelligent System", style="bold white")

        panel = Panel(
            startup_text,
            title="🤖 AI Assistant Initializing",
            border_style="cyan",
            padding=(1, 2)
        )

        console.print(panel)
        console.print(f"{Fore.CYAN}[JARVIS]{Style.RESET_ALL} System initialized. Say 'Hey Jarvis' to activate.", style="bold")
        self.speak("Jarvis AI Assistant initialized. How may I assist you today, Sir?")

    def speak(self, text):
        """Convert text to speech"""
        try:
            console.print(f"{Fore.BLUE}[JARVIS]{Style.RESET_ALL} {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            console.print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Speech synthesis error: {e}")

    def listen(self):
        """Listen for voice commands"""
        try:
            with self.microphone as source:
                console.print(f"{Fore.GREEN}[LISTENING]{Style.RESET_ALL} Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            while self.is_active:
                try:
                    with self.microphone as source:
                        console.print(f"{Fore.GREEN}[LISTENING]{Style.RESET_ALL} Waiting for command...")
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                    command = self.recognizer.recognize_google(audio).lower()
                    console.print(f"{Fore.YELLOW}[USER]{Style.RESET_ALL} {command}")

                    # Check for wake words
                    if any(wake_word in command for wake_word in self.wake_words):
                        self.is_listening = True
                        self.speak("Yes, Sir?")
                        continue

                    # Check for goodbye words
                    if any(goodbye_word in command for goodbye_word in self.goodbye_words):
                        self.speak("Goodbye, Sir. Jarvis going offline.")
                        self.is_active = False
                        break

                    # Process command if listening
                    if self.is_listening:
                        self.process_command(command)
                        self.is_listening = False

                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    if self.is_listening:
                        self.speak("I didn't catch that, Sir. Could you repeat?")
                        self.is_listening = False
                except sr.RequestError as e:
                    console.print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Could not request results: {e}")

        except Exception as e:
            console.print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Microphone error: {e}")
            self.speak("I'm having trouble with the audio system, Sir.")

    def process_command(self, command):
        """Process voice commands"""
        try:
            # Time and date commands
            if any(word in command for word in ['time', 'what time']):
                self.tell_time()

            elif any(word in command for word in ['date', 'what date', 'today']):
                self.tell_date()

            # Weather commands
            elif 'weather' in command:
                self.get_weather()

            # Search commands
            elif any(word in command for word in ['search', 'google', 'look up']):
                self.web_search(command)

            # Wikipedia commands
            elif 'wikipedia' in command or 'wiki' in command:
                self.wikipedia_search(command)

            # System commands
            elif any(word in command for word in ['system status', 'system info', 'computer status']):
                self.system_status()

            # Open applications
            elif 'open' in command:
                self.open_application(command)

            # News commands
            elif 'news' in command:
                self.get_news()

            # Math and calculations
            elif any(word in command for word in ['calculate', 'math', 'compute']):
                self.calculate(command)

            # AI chat (if OpenAI API available)
            elif self.openai_api_key:
                self.ai_chat(command)

            else:
                self.speak("I'm not sure how to help with that, Sir. Could you try rephrasing?")

        except Exception as e:
            console.print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Command processing error: {e}")
            self.speak("I encountered an error processing that command, Sir.")

    def tell_time(self):
        """Tell current time"""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speak(f"The time is {current_time}, Sir.")

    def tell_date(self):
        """Tell current date"""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self.speak(f"Today is {current_date}, Sir.")

    def get_weather(self):
        """Get weather information"""
        try:
            # Simple weather API call (you can replace with your preferred weather service)
            self.speak("I would need a weather API key to provide current weather information, Sir. For now, I recommend checking your local weather app.")
        except Exception as e:
            self.speak("I'm unable to retrieve weather information at the moment, Sir.")

    def web_search(self, command):
        """Perform web search"""
        try:
            search_terms = command.replace('search', '').replace('google', '').replace('look up', '').strip()
            if search_terms:
                url = f"https://www.google.com/search?q={search_terms}"
                webbrowser.open(url)
                self.speak(f"I've opened a web search for {search_terms}, Sir.")
            else:
                self.speak("What would you like me to search for, Sir?")
        except Exception as e:
            self.speak("I'm unable to open the web browser, Sir.")

    def wikipedia_search(self, command):
        """Search Wikipedia"""
        try:
            search_terms = command.replace('wikipedia', '').replace('wiki', '').strip()
            if search_terms:
                try:
                    summary = wikipedia.summary(search_terms, sentences=2)
                    self.speak(f"According to Wikipedia: {summary}")
                except wikipedia.exceptions.DisambiguationError as e:
                    self.speak(f"Multiple results found for {search_terms}. Please be more specific, Sir.")
                except wikipedia.exceptions.PageError:
                    self.speak(f"No Wikipedia page found for {search_terms}, Sir.")
            else:
                self.speak("What would you like me to look up on Wikipedia, Sir?")
        except Exception as e:
            self.speak("I'm unable to access Wikipedia at the moment, Sir.")

    def system_status(self):
        """Get system status"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            status = f"System status: CPU usage is {cpu_percent}%. "
            status += f"Memory usage is {memory.percent}%. "
            status += f"Disk usage is {disk.percent}%."

            self.speak(status)
        except Exception as e:
            self.speak("I'm unable to retrieve system information, Sir.")

    def open_application(self, command):
        """Open applications"""
        try:
            if 'browser' in command or 'firefox' in command:
                subprocess.Popen(['firefox'])
                self.speak("Opening Firefox browser, Sir.")
            elif 'terminal' in command:
                subprocess.Popen(['gnome-terminal'])
                self.speak("Opening terminal, Sir.")
            elif 'calculator' in command:
                subprocess.Popen(['gnome-calculator'])
                self.speak("Opening calculator, Sir.")
            elif 'file manager' in command or 'files' in command:
                subprocess.Popen(['nautilus'])
                self.speak("Opening file manager, Sir.")
            else:
                self.speak("I'm not sure which application you'd like me to open, Sir.")
        except Exception as e:
            self.speak("I'm unable to open that application, Sir.")

    def get_news(self):
        """Get news headlines"""
        try:
            self.speak("I would need a news API key to provide current headlines, Sir. For now, I recommend checking your preferred news website.")
        except Exception as e:
            self.speak("I'm unable to retrieve news at the moment, Sir.")

    def calculate(self, command):
        """Perform calculations"""
        try:
            # Extract mathematical expression
            import re
            math_expression = re.findall(r'[\d+\-*/\(\)\.\s]+', command)
            if math_expression:
                expression = ''.join(math_expression).strip()
                # Simple evaluation (be careful with eval in production)
                result = eval(expression)
                self.speak(f"The result is {result}, Sir.")
            else:
                self.speak("I didn't understand the mathematical expression, Sir.")
        except Exception as e:
            self.speak("I'm unable to perform that calculation, Sir.")

    def ai_chat(self, command):
        """AI-powered conversation using OpenAI"""
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"You are Jarvis, Tony Stark's AI assistant. Respond as Jarvis would: {command}",
                max_tokens=150,
                temperature=0.7
            )
            reply = response.choices[0].text.strip()
            self.speak(reply)
        except Exception as e:
            # Fallback responses without OpenAI
            fallback_responses = [
                "I understand, Sir. How else may I assist you?",
                "Interesting perspective, Sir. Is there anything specific you'd like me to help with?",
                "Noted, Sir. What would you like me to do next?",
                "I'm here to help, Sir. What do you need assistance with?"
            ]
            import random
            self.speak(random.choice(fallback_responses))

    def run(self):
        """Main run loop"""
        try:
            # Start listening in a separate thread
            listen_thread = threading.Thread(target=self.listen)
            listen_thread.daemon = True
            listen_thread.start()

            # Keep main thread alive
            while self.is_active:
                time.sleep(0.1)

        except KeyboardInterrupt:
            console.print(f"\n{Fore.CYAN}[JARVIS]{Style.RESET_ALL} Shutting down...")
            self.speak("Goodbye, Sir. Jarvis shutting down.")
            self.is_active = False

def main():
    """Main function"""
    try:
        jarvis = JarvisAI()
        jarvis.run()
    except Exception as e:
        console.print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to initialize Jarvis: {e}")
        print("Please ensure all dependencies are installed and try again.")

if __name__ == "__main__":
    main()