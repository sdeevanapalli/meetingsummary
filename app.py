"""
Meeting Minutes Generator - Streamlit App (macOS Optimized)
A reliable and cost-effective solution for recording and transcribing meetings
"""

import streamlit as st
import speech_recognition as sr
import io
import time
from datetime import datetime
import tempfile
import os
import docx
import PyPDF2
import re
from audio_recorder_streamlit import audio_recorder

# Page configuration
st.set_page_config(
    page_title="Meeting Minutes Generator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .transcript-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

def read_uploaded_file(uploaded_file):
    """Read content from uploaded file"""
    try:
        if uploaded_file.type == "text/plain":
            content = str(uploaded_file.read(), "utf-8")
            return content
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
            return content
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def transcribe_audio(audio_bytes):
    """Transcribe audio bytes to text using speech recognition"""
    try:
        # Save audio bytes to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            # Use speech recognition
            r = sr.Recognizer()
            with sr.AudioFile(tmp_file.name) as source:
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.record(source)
                
                try:
                    # Try Google Speech Recognition (free)
                    text = r.recognize_google(audio, language='en-US')
                    return text, "success"
                except sr.UnknownValueError:
                    return "Could not understand the audio clearly. Please speak louder and more clearly.", "warning"
                except sr.RequestError as e:
                    return f"Could not connect to speech recognition service. Check internet connection. Error: {e}", "error"
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(tmp_file.name)
                    except:
                        pass
                        
    except Exception as e:
        return f"Transcription error: {str(e)}", "error"

def generate_meeting_minutes(transcript, agenda="", attendees=[]):
    """Generate formatted meeting minutes"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    minutes = f"""MEETING MINUTES
==================

Date: {date_str}
Time: {time_str}

"""
    
    if agenda:
        minutes += f"""AGENDA:
{agenda}

"""
    
    if attendees:
        minutes += f"""ATTENDEES:
{', '.join(attendees)}

"""
    
    # Extract key points (simple implementation)
    sentences = re.split(r'[.!?]+', transcript)
    key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:5]
    
    minutes += """DISCUSSION SUMMARY:
"""
    
    for i, sentence in enumerate(key_sentences, 1):
        if sentence:
            minutes += f"{i}. {sentence.strip()}\n"
    
    minutes += f"""

FULL TRANSCRIPT:
================
{transcript}
"""
    
    return minutes

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎤 Meeting Minutes Generator</h1>
        <p>Record, transcribe, and generate professional meeting minutes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'transcript_history' not in st.session_state:
        st.session_state.transcript_history = []
    if 'full_transcript' not in st.session_state:
        st.session_state.full_transcript = ""
    if 'agenda' not in st.session_state:
        st.session_state.agenda = ""
    if 'minutes' not in st.session_state:
        st.session_state.minutes = ""
    
    # Sidebar for controls and agenda
    with st.sidebar:
        st.header("📋 Meeting Setup")
        
        # macOS Permission Notice
        st.markdown("""
        <div class="status-box warning-box">
            <strong>🔒 macOS Users:</strong><br>
            Make sure to allow microphone access when prompted.<br>
            Go to System Settings → Privacy & Security → Microphone if needed.
        </div>
        """, unsafe_allow_html=True)
        
        # Agenda upload
        st.subheader("Upload Agenda")
        uploaded_file = st.file_uploader(
            "Choose agenda file",
            type=['txt', 'pdf', 'docx'],
            help="Upload your meeting agenda for better minutes generation"
        )
        
        if uploaded_file is not None:
            st.session_state.agenda = read_uploaded_file(uploaded_file)
            st.success(f"Agenda loaded from {uploaded_file.name}")
        
        # Attendees
        st.subheader("Meeting Attendees")
        attendees_input = st.text_area(
            "Enter attendee names (one per line)",
            help="List all meeting participants",
            value="Speaker 1\nSpeaker 2"
        )
        attendees = [name.strip() for name in attendees_input.split('\n') if name.strip()]
        
        # Clear transcript
        if st.button("🗑️ Clear All Transcripts", type="secondary"):
            st.session_state.transcript_history = []
            st.session_state.full_transcript = ""
            st.session_state.minutes = ""
            st.rerun()
        
        # Cost info
        st.markdown("""
        ### 💡 Cost-Effective Features:
        - Uses Google's free speech recognition API
        - Local audio processing
        - No subscription fees
        - Works offline for file processing
        - Multi-format support (PDF, DOCX, TXT)
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🎙️ Audio Recording")
        
        # Instructions
        st.markdown("""
        <div class="status-box info-box">
            <strong>How to record:</strong><br>
            1. Click the microphone button below<br>
            2. Speak clearly (you'll see a recording indicator)<br>
            3. Click stop when finished<br>
            4. Audio will be automatically transcribed
        </div>
        """, unsafe_allow_html=True)
        
        # Audio recorder component
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e74c3c",
            neutral_color="#2c3e50",
            icon_name="microphone",
            icon_size="2x",
            pause_threshold=2.0,
            sample_rate=41_000
        )
        
        # Process recorded audio
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            with st.spinner("🔄 Transcribing your audio..."):
                transcript, status = transcribe_audio(audio_bytes)
                
                # Display result based on status
                if status == "success":
                    st.markdown(f"""
                    <div class="status-box success-box">
                        <strong>✅ Transcription successful!</strong><br>
                        "{transcript}"
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add to transcript history
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    speaker_num = len(st.session_state.transcript_history) % 2 + 1
                    entry = f"[{timestamp}] Speaker {speaker_num}: {transcript}"
                    st.session_state.transcript_history.append(entry)
                    
                    # Update full transcript
                    st.session_state.full_transcript = "\n".join(st.session_state.transcript_history)
                    
                elif status == "warning":
                    st.markdown(f"""
                    <div class="status-box warning-box">
                        <strong>⚠️ Transcription issue:</strong><br>
                        {transcript}
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:  # error
                    st.markdown(f"""
                    <div class="status-box error-box">
                        <strong>❌ Transcription failed:</strong><br>
                        {transcript}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Generate minutes button
        if st.session_state.full_transcript:
            if st.button("📝 Generate Meeting Minutes", type="primary", use_container_width=True):
                with st.spinner("Generating meeting minutes..."):
                    st.session_state.minutes = generate_meeting_minutes(
                        st.session_state.full_transcript, 
                        st.session_state.agenda, 
                        attendees
                    )
                st.success("Meeting minutes generated successfully!")
                st.rerun()
    
    with col2:
        st.header("📄 Agenda Preview")
        if st.session_state.agenda:
            st.text_area("Meeting Agenda", st.session_state.agenda, height=300, disabled=True)
        else:
            st.info("Upload an agenda file to see preview here")
            st.markdown("""
            **Sample agenda format:**
            ```
            1. Welcome and introductions
            2. Review of previous meeting
            3. Current project status
            4. Budget discussion
            5. Next steps
            6. Questions and answers
            ```
            """)
    
    # Transcript and Minutes section
    st.header("📝 Transcript & Minutes")
    
    tab1, tab2 = st.tabs(["📋 Live Transcript", "📄 Meeting Minutes"])
    
    with tab1:
        if st.session_state.full_transcript:
            st.markdown(f"""
            <div class="transcript-box">
{st.session_state.full_transcript}
            </div>
            """, unsafe_allow_html=True)
            
            # Download transcript
            st.download_button(
                label="⬇️ Download Transcript",
                data=st.session_state.full_transcript,
                file_name=f"meeting_transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("🎤 Start recording to see transcript here. Each recording will be added as a new entry.")
    
    with tab2:
        if st.session_state.minutes:
            st.text_area("Generated Minutes", st.session_state.minutes, height=400, disabled=True)
            
            # Download minutes
            st.download_button(
                label="⬇️ Download Meeting Minutes",
                data=st.session_state.minutes,
                file_name=f"meeting_minutes_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("📝 Generate meeting minutes from your transcript to see them here")
    
    # Instructions
    with st.expander("📖 Detailed Instructions & Troubleshooting"):
        st.markdown("""
        ### 🚀 Quick Start Guide:
        
        1. **🔒 Grant Permissions**: Allow microphone access when prompted
        2. **📋 Upload Agenda**: (Optional) Upload your meeting agenda 
        3. **👥 Add Attendees**: List meeting participants
        4. **🎙️ Record**: Click the microphone button and speak clearly
        5. **📝 Generate**: Click "Generate Meeting Minutes" when done
        6. **⬇️ Download**: Save both transcript and formatted minutes
        
        ### 🔧 Troubleshooting:
        
        **🎤 Microphone Issues:**
        - Check System Settings → Privacy & Security → Microphone
        - Ensure your browser has microphone permission
        - Try refreshing the page if permissions were just granted
        
        **🔊 Audio Quality:**
        - Speak clearly and at normal volume
        - Minimize background noise
        - Stay close to your microphone
        - Pause between speakers for better detection
        
        **🌐 Internet Issues:**
        - Speech recognition requires internet connection
        - Check your network connection
        - Try again if you see connection errors
        
        ### 💡 Pro Tips:
        - Record in shorter segments for better accuracy
        - Use the "Clear All Transcripts" button to start fresh
        - Upload agenda first for better meeting minutes
        - Each recording adds to your running transcript
        - Download frequently to avoid losing work
        
        ### 🖥️ System Requirements:
        - **macOS**: 10.14+ with microphone permission
        - **Browser**: Chrome, Safari, or Firefox
        - **Internet**: Required for speech recognition
        - **Microphone**: Built-in or external microphone
        """)

if __name__ == "__main__":
    main()