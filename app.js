/**
 * Meeting Minutes Generator Application
 * A cost-effective solution for recording, transcribing, and generating meeting minutes
 */

class MeetingMinutesApp {
    constructor() {
        // Application state
        this.isRecording = false;
        this.recognition = null;
        this.transcript = '';
        this.speakers = new Map();
        this.currentSpeaker = 1;
        this.agenda = '';
        this.minutes = '';
        this.lastSpeechTime = Date.now();
        
        // Initialize the application
        this.initializeElements();
        this.setupEventListeners();
        this.initializeSpeechRecognition();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.recordBtn = document.getElementById('recordBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.generateBtn = document.getElementById('generateBtn');
        this.status = document.getElementById('status');
        this.recordingIndicator = document.getElementById('recordingIndicator');
        this.transcriptDiv = document.getElementById('transcript');
        this.fileUpload = document.getElementById('fileUpload');
        this.fileInput = document.getElementById('fileInput');
        this.agendaContent = document.getElementById('agendaContent');
        this.downloadTranscript = document.getElementById('downloadTranscript');
        this.downloadMinutes = document.getElementById('downloadMinutes');
    }

    /**
     * Setup event listeners for all interactive elements
     */
    setupEventListeners() {
        // Recording controls
        this.recordBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
        this.generateBtn.addEventListener('click', () => this.generateMinutes());
        
        // File upload handlers
        this.fileUpload.addEventListener('click', () => this.fileInput.click());
        this.fileUpload.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.fileUpload.addEventListener('drop', (e) => this.handleDrop(e));
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Download handlers
        this.downloadTranscript.addEventListener('click', () => this.downloadFile('transcript'));
        this.downloadMinutes.addEventListener('click', () => this.downloadFile('minutes'));
    }

    /**
     * Initialize Web Speech API for speech recognition
     */
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure speech recognition
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            
            // Event handlers for speech recognition
            this.recognition.onstart = () => {
                this.updateStatus('Recording started. Speak clearly into your microphone.');
                this.recordingIndicator.classList.add('active');
            };
            
            this.recognition.onresult = (event) => {
                this.processSpeechResult(event);
            };
            
            this.recognition.onerror = (event) => {
                this.updateStatus(`Error: ${event.error}`);
            };
            
            this.recognition.onend = () => {
                if (this.isRecording) {
                    this.recognition.start(); // Restart if still recording
                }
            };
        } else {
            this.updateStatus('Speech recognition not supported in this browser.');
        }
    }

    /**
     * Process speech recognition results
     * @param {SpeechRecognitionEvent} event - The speech recognition event
     */
    processSpeechResult(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        // Process all results from the current event
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            const confidence = event.results[i][0].confidence;
            
            console.log(`Result ${i}: "${transcript}" (confidence: ${confidence}, final: ${event.results[i].isFinal})`);
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Show interim results in real-time
        if (interimTranscript) {
            const tempDiv = document.createElement('div');
            tempDiv.style.opacity = '0.6';
            tempDiv.style.fontStyle = 'italic';
            tempDiv.textContent = `Speaking: ${interimTranscript}`;
            
            // Remove previous interim results
            const existingInterim = this.transcriptDiv.querySelector('.interim-result');
            if (existingInterim) {
                existingInterim.remove();
            }
            
            tempDiv.classList.add('interim-result');
            this.transcriptDiv.appendChild(tempDiv);
        }
        
        // Add final transcript to the meeting record
        if (finalTranscript.trim()) {
            // Remove interim results
            const existingInterim = this.transcriptDiv.querySelector('.interim-result');
            if (existingInterim) {
                existingInterim.remove();
            }
            
            this.addToTranscript(finalTranscript.trim());
            this.updateStatus('🎙️ Recording... Speech detected and transcribed!');
        }
    }

    /**
     * Add text to the transcript with speaker detection and timestamp
     * @param {string} text - The transcribed text to add
     */
    addToTranscript(text) {
        if (!text) return;
        
        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        
        // Simple speaker detection based on silence gaps
        const timeSinceLastSpeech = Date.now() - this.lastSpeechTime;
        if (timeSinceLastSpeech > 5000) { // 5 seconds silence suggests new speaker
            this.currentSpeaker = this.currentSpeaker === 1 ? 2 : 1;
        }
        
        this.lastSpeechTime = Date.now();
        
        // Format the transcript entry
        const entry = `\n[${timestamp}] Speaker ${this.currentSpeaker}: ${text}\n`;
        this.transcript += entry;
        
        // Update the display
        this.transcriptDiv.innerHTML = this.formatTranscript(this.transcript);
        this.transcriptDiv.scrollTop = this.transcriptDiv.scrollHeight;
    }

    /**
     * Format transcript text with HTML styling
     * @param {string} transcript - Raw transcript text
     * @returns {string} HTML formatted transcript
     */
    formatTranscript(transcript) {
        return transcript
            .replace(/\[([^\]]+)\]/g, '<span class="timestamp">[$1]</span>')
            .replace(/Speaker (\d+):/g, '<span class="speaker">Speaker $1:</span>');
    }

    /**
     * Start recording audio and speech recognition
     */
    startRecording() {
        if (!this.recognition) {
            this.updateStatus('Speech recognition not available.');
            return;
        }
        
        this.isRecording = true;
        this.transcript = '';
        this.transcriptDiv.textContent = 'Starting recording...';
        
        // Update button states
        this.recordBtn.disabled = true;
        this.stopBtn.disabled = false;
        
        // Start speech recognition
        this.recognition.start();
    }

    /**
     * Stop recording and prepare for minutes generation
     */
    stopRecording() {
        this.isRecording = false;
        
        // Stop speech recognition
        if (this.recognition) {
            this.recognition.stop();
        }
        
        // Update button states
        this.recordBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.generateBtn.disabled = false;
        this.downloadTranscript.disabled = false;
        
        // Hide recording indicator
        this.recordingIndicator.classList.remove('active');
        this.updateStatus('Recording stopped. You can now generate meeting minutes.');
    }

    /**
     * Generate structured meeting minutes from the transcript
     */
    generateMinutes() {
        if (!this.transcript.trim()) {
            this.updateStatus('No transcript available to generate minutes.');
            return;
        }
        
        this.updateStatus('Generating meeting minutes...');
        
        // Simulate processing time for better UX
        setTimeout(() => {
            this.minutes = this.createMeetingMinutes();
            this.displayMinutes();
            this.downloadMinutes.disabled = false;
            this.updateStatus('Meeting minutes generated successfully!');
        }, 2000);
    }

    /**
     * Create formatted meeting minutes from transcript and agenda
     * @returns {string} Formatted meeting minutes
     */
    createMeetingMinutes() {
        const now = new Date();
        const date = now.toLocaleDateString();
        const time = now.toLocaleTimeString();
        
        let minutes = `MEETING MINUTES\n`;
        minutes += `==================\n\n`;
        minutes += `Date: ${date}\n`;
        minutes += `Time: ${time}\n\n`;
        
        // Add agenda if available
        if (this.agenda.trim()) {
            minutes += `AGENDA:\n`;
            minutes += `${this.agenda}\n\n`;
        }
        
        // Add attendees section
        minutes += `ATTENDEES:\n`;
        minutes += `- Speaker 1\n`;
        minutes += `- Speaker 2\n\n`;
        
        // Add discussion summary
        minutes += `DISCUSSION SUMMARY:\n`;
        minutes += this.extractKeyPoints();
        
        // Add full transcript
        minutes += `\n\nFULL TRANSCRIPT:\n`;
        minutes += `=================\n`;
        minutes += this.transcript;
        
        return minutes;
    }

    /**
     * Extract key points from the discussion for summary
     * @returns {string} Formatted key points
     */
    extractKeyPoints() {
        // Simple keyword extraction for demo purposes
        const sentences = this.transcript.split(/[.!?]+/).filter(s => s.trim().length > 20);
        const keyPoints = sentences.slice(0, 5).map((sentence, index) => {
            return `${index + 1}. ${sentence.replace(/\[[^\]]+\]|\bSpeaker \d+:/g, '').trim()}\n`;
        }).join('');
        
        return keyPoints || 'No key points extracted from the discussion.\n';
    }

    /**
     * Display generated minutes in the transcript area
     */
    displayMinutes() {
        this.transcriptDiv.innerHTML = `<div style="white-space: pre-wrap; font-family: 'Segoe UI', sans-serif;">${this.minutes}</div>`;
    }

    /**
     * Handle drag over event for file upload
     * @param {DragEvent} e - Drag event
     */
    handleDragOver(e) {
        e.preventDefault();
        this.fileUpload.classList.add('dragover');
    }

    /**
     * Handle file drop event
     * @param {DragEvent} e - Drop event
     */
    handleDrop(e) {
        e.preventDefault();
        this.fileUpload.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    /**
     * Handle file selection from input
     * @param {Event} e - File input change event
     */
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    /**
     * Process uploaded agenda file
     * @param {File} file - The uploaded file
     */
    async processFile(file) {
        const fileType = file.type;
        const fileName = file.name.toLowerCase();
        
        try {
            if (fileName.endsWith('.txt')) {
                this.agenda = await this.readTextFile(file);
            } else if (fileName.endsWith('.pdf')) {
                this.updateStatus('PDF processing would require additional API integration.');
                this.agenda = 'PDF file uploaded (processing not implemented in demo)';
            } else if (fileName.endsWith('.docx')) {
                this.updateStatus('DOCX processing would require additional library integration.');
                this.agenda = 'DOCX file uploaded (processing not implemented in demo)';
            }
            
            this.agendaContent.textContent = this.agenda;
            this.updateStatus(`Agenda loaded from ${file.name}`);
        } catch (error) {
            this.updateStatus(`Error processing file: ${error.message}`);
        }
    }

    /**
     * Read text file content
     * @param {File} file - Text file to read
     * @returns {Promise<string>} File content as string
     */
    readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    /**
     * Download file (transcript or minutes)
     * @param {string} type - Type of file to download ('transcript' or 'minutes')
     */
    downloadFile(type) {
        const content = type === 'transcript' ? this.transcript : this.minutes;
        const filename = type === 'transcript' ? 'meeting_transcript.txt' : 'meeting_minutes.txt';
        
        // Create and trigger download
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Update status message
     * @param {string} message - Status message to display
     */
    updateStatus(message) {
        this.status.textContent = message;
    }
}

/**
 * Initialize the application when the DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    new MeetingMinutesApp();
});

/**
 * Export for potential module usage
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MeetingMinutesApp;
}