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
from dotenv import load_dotenv
import openai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Page configuration
st.set_page_config(
    page_title="Meeting Minutes Generator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - FIXED
st.markdown("""
<style>
    /* Responsive meta tag for mobile scaling */
    @media (max-width: 600px) {
        html, body, .main-header, .status-box, .transcript-box, .agenda-box {
            font-size: 1.05rem !important;
        }
        .main-header {
            padding: 1rem 0 !important;
        }
        .transcript-box, .agenda-box {
            max-height: 250px !important;
            font-size: 0.98rem !important;
        }
        .stTextArea textarea, .stButton button {
            font-size: 1.1rem !important;
            min-height: 48px !important;
        }
        .stButton button, .stDownloadButton button {
            min-width: 0 !important;
        }
    }
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
        color: #222 !important;
        box-sizing: border-box;
    }
    .agenda-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        max-height: 300px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        color: #222 !important;
        box-sizing: border-box;
    }
    .stTextArea textarea, .stButton button, .stDownloadButton button {
        border-radius: 8px !important;
        font-size: 1.08rem !important;
        min-height: 44px !important;
        box-sizing: border-box;
    }
    .stButton button, .stDownloadButton button {
        width: 100% !important;
        min-width: 0 !important;
        margin-bottom: 0.5rem !important;
    }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1">
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
    """Generate formatted meeting minutes - FIXED INDENTATION"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    minutes = (
        f"MEETING MINUTES\n"
        f"==================\n\n"
        f"Date: {date_str}\n"
        f"Time: {time_str}\n\n"
    )
    
    if agenda:
        minutes += f"AGENDA:\n{agenda}\n\n"
    if attendees:
        minutes += f"ATTENDEES:\n{', '.join(attendees)}\n\n"

    # Use OpenAI to generate summary if API key is available (v1.x API)
    summary = None
    if OPENAI_API_KEY:
        try:
            prompt = (
                "You are an expert meeting assistant. Summarize the following meeting transcript into 3-5 concise bullet points, focusing on the main discussion and decisions.\n\n"
                f"Transcript:\n{transcript}\n\nSummary:"
            )
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.4,
            )
            summary = response.choices[0].message.content.strip()
        except Exception as e:
            summary = f"Error generating AI summary: {str(e)}"
    
    minutes += "DISCUSSION SUMMARY:\n"
    if isinstance(summary, str) and summary.strip():
        minutes += summary.strip() + "\n\n"
    else:
        minutes += "Summary not available now, try again or contact developer.\n\n"

    minutes += (
        f"FULL TRANSCRIPT:\n"
        f"================\n"
        f"{transcript}\n"
    )
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

    # Agenda preview
    st.subheader("Agenda Preview")
    if st.session_state.agenda:
        st.markdown(f"""
        <div class="agenda-box">{st.session_state.agenda}</div>
        """, unsafe_allow_html=True)
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

    # Attendees
    st.subheader("Meeting Attendees")
    attendees_input = st.text_area(
        "Enter attendee names (one per line)",
        help="List all meeting participants",
        value=""
    )
    attendees = [name.strip() for name in attendees_input.split('\n') if name.strip()]

    # Clear transcript
    if st.button("🗑️ Clear All Transcripts", type="secondary"):
        st.session_state.transcript_history = []
        st.session_state.full_transcript = ""
        st.session_state.minutes = ""
        st.rerun()
    
    # Audio Recording Section
    st.header("🎙️ Audio Recording")
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

    # Prevent duplicate transcript entries by tracking last processed audio
    if 'last_audio_bytes' not in st.session_state:
        st.session_state.last_audio_bytes = None

    if audio_bytes and (audio_bytes != st.session_state.last_audio_bytes):
        st.audio(audio_bytes, format="audio/wav")
        with st.spinner("🔄 Transcribing your audio..."):
            transcript, status = transcribe_audio(audio_bytes)
            if status == "success":
                st.markdown(f"""
                <div class="status-box success-box">
                    <strong>✅ Transcription successful!</strong><br>
                    "{transcript}"
                </div>
                """, unsafe_allow_html=True)
                timestamp = datetime.now().strftime("%H:%M:%S")
                entry = f"[{timestamp}] {transcript}"
                st.session_state.transcript_history.append(entry)
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
        st.session_state.last_audio_bytes = audio_bytes

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
    
    # Transcript and Minutes section
    st.header("📝 Transcript & Minutes")
    if st.session_state.full_transcript:
        st.subheader("📋 Live Transcript")
        st.markdown(f"""
        <div class="transcript-box">
{st.session_state.full_transcript}
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download Transcript",
            data=st.session_state.full_transcript,
            file_name=f"meeting_transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("🎤 Start recording to see transcript here. Each recording will be added as a new entry.")

    if st.session_state.minutes:
        st.subheader("📄 Meeting Minutes")
        st.text_area("Generated Minutes", st.session_state.minutes, height=400, disabled=True)
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