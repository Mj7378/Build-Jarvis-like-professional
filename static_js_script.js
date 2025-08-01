// JARVIS AI Assistant JavaScript

class JarvisInterface {
    constructor() {
        this.socket = io();
        this.isListening = false;
        this.recognition = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.setupSpeechRecognition();
        this.updateTimestamp();
        this.startSystemMonitoring();

        // Show initial timestamp
        this.updateInitialTimestamp();
    }

    setupEventListeners() {
        // Send button
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendCommand();
        });

        // Enter key in input
        document.getElementById('commandInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendCommand();
            }
        });

        // Voice button
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.toggleVoiceRecognition();
        });

        // Quick action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.currentTarget.dataset.command;
                this.sendCommand(command);
            });
        });
    }

    setupWebSocket() {
        this.socket.on('connect', () => {
            console.log('Connected to Jarvis');
            this.updateStatus('ONLINE', 'online');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from Jarvis');
            this.updateStatus('OFFLINE', 'offline');
        });

        this.socket.on('response', (data) => {
            this.addMessage(data.response, 'jarvis', data.timestamp);
        });

        this.socket.on('status', (data) => {
            console.log('Status:', data);
        });
    }

    setupSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();

            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                console.log('Voice recognition started');
                this.showAudioVisualizer(true);
            };

            this.recognition.onend = () => {
                console.log('Voice recognition ended');
                this.isListening = false;
                this.updateVoiceButton(false);
                this.showAudioVisualizer(false);
            };

            this.recognition.onresult = (event) => {
                const command = event.results[0][0].transcript;
                console.log('Voice command:', command);
                this.sendCommand(command);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListening = false;
                this.updateVoiceButton(false);
                this.showAudioVisualizer(false);
            };
        } else {
            console.warn('Speech recognition not supported');
            document.getElementById('voiceBtn').style.display = 'none';
        }
    }

    sendCommand(command = null) {
        const input = document.getElementById('commandInput');
        const commandText = command || input.value.trim();

        if (!commandText) return;

        // Clear input if using manual input
        if (!command) {
            input.value = '';
        }

        // Add user message
        this.addMessage(commandText, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        // Send via WebSocket
        this.socket.emit('command', { command: commandText });

        // Also send via API for backup
        fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                command: commandText,
                speak: false 
            }),
        })
        .then(response => response.json())
        .then(data => {
            this.hideTypingIndicator();
            if (data.status === 'success') {
                // Response handled via WebSocket
                console.log('Command processed successfully');
            } else {
                this.addMessage('Error processing command', 'jarvis');
            }
        })
        .catch(error => {
            this.hideTypingIndicator();
            console.error('Error:', error);
            this.addMessage('Connection error occurred', 'jarvis');
        });
    }

    addMessage(text, sender, timestamp = null) {
        const chatContainer = document.getElementById('chatContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const icon = sender === 'jarvis' ? 'fas fa-robot' : 'fas fa-user';
        const time = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();

        messageDiv.innerHTML = `
            <div class="message-content">
                <i class="${icon}"></i>
                <span>${text}</span>
            </div>
            <div class="timestamp">${time}</div>
        `;

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Add glow effect
        messageDiv.classList.add('glow');
        setTimeout(() => {
            messageDiv.classList.remove('glow');
        }, 2000);
    }

    showTypingIndicator() {
        const chatContainer = document.getElementById('chatContainer');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message jarvis-message typing-indicator';
        typingDiv.id = 'typingIndicator';

        typingDiv.innerHTML = `
            <div class="message-content">
                <i class="fas fa-robot"></i>
                <span>Jarvis is thinking</span>
                <div class="loading"></div>
            </div>
        `;

        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    toggleVoiceRecognition() {
        if (!this.recognition) {
            this.addMessage('Voice recognition not supported in this browser', 'jarvis');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.isListening = true;
            this.updateVoiceButton(true);
            this.recognition.start();
        }
    }

    updateVoiceButton(active) {
        const voiceBtn = document.getElementById('voiceBtn');
        if (active) {
            voiceBtn.classList.add('active');
        } else {
            voiceBtn.classList.remove('active');
        }
    }

    showAudioVisualizer(show) {
        const visualizer = document.getElementById('audioVisualizer');
        if (show) {
            visualizer.classList.add('active');
        } else {
            visualizer.classList.remove('active');
        }
    }

    updateStatus(text, status) {
        const statusText = document.getElementById('statusText');
        const statusLight = document.getElementById('statusLight');

        statusText.textContent = text;
        statusLight.className = `status-light ${status}`;
    }

    updateTimestamp() {
        const timestamps = document.querySelectorAll('.timestamp:empty');
        const now = new Date().toLocaleTimeString();
        timestamps.forEach(timestamp => {
            timestamp.textContent = now;
        });
    }

    updateInitialTimestamp() {
        const timestamp = document.querySelector('.timestamp');
        if (timestamp && !timestamp.textContent) {
            timestamp.textContent = new Date().toLocaleTimeString();
        }
    }

    startSystemMonitoring() {
        // Simulate system monitoring (in real implementation, this would come from backend)
        setInterval(() => {
            this.updateSystemStats();
        }, 3000);

        // Initial update
        this.updateSystemStats();
    }

    updateSystemStats() {
        // Simulate system stats (replace with real data from backend)
        const cpuUsage = Math.floor(Math.random() * 30) + 10; // 10-40%
        const memoryUsage = Math.floor(Math.random() * 40) + 30; // 30-70%
        const diskUsage = Math.floor(Math.random() * 20) + 60; // 60-80%

        this.updateProgressBar('cpuProgress', 'cpuValue', cpuUsage);
        this.updateProgressBar('memoryProgress', 'memoryValue', memoryUsage);
        this.updateProgressBar('diskProgress', 'diskValue', diskUsage);
    }

    updateProgressBar(progressId, valueId, percentage) {
        const progressBar = document.getElementById(progressId);
        const valueSpan = document.getElementById(valueId);

        if (progressBar && valueSpan) {
            progressBar.style.width = `${percentage}%`;
            valueSpan.textContent = `${percentage}%`;

            // Change color based on usage
            let color;
            if (percentage < 50) {
                color = 'linear-gradient(90deg, #00d4ff, #00ff88)';
            } else if (percentage < 80) {
                color = 'linear-gradient(90deg, #ffaa00, #ff6600)';
            } else {
                color = 'linear-gradient(90deg, #ff4500, #ff0000)';
            }
            progressBar.style.background = color;
        }
    }

    // Add some interactive effects
    addInteractiveEffects() {
        // Add hover effects to panels
        document.querySelectorAll('.panel').forEach(panel => {
            panel.addEventListener('mouseenter', () => {
                panel.style.transform = 'translateY(-5px) scale(1.02)';
            });

            panel.addEventListener('mouseleave', () => {
                panel.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Add click effect to buttons
        document.querySelectorAll('.action-btn, .send-btn, .voice-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const ripple = document.createElement('div');
                ripple.className = 'ripple';
                ripple.style.left = e.offsetX + 'px';
                ripple.style.top = e.offsetY + 'px';
                btn.appendChild(ripple);

                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }
}

// Initialize Jarvis when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 Initializing Jarvis Interface...');
    window.jarvis = new JarvisInterface();

    // Add some startup animation
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 500);
});

// Add some CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(0, 212, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .status-light.online {
        background: #00ff00;
        box-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00;
    }
    
    .status-light.offline {
        background: #ff0000;
        box-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000;
    }
`;
document.head.appendChild(style);