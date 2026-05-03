import streamlit as st
import speech_recognition as sr
import io
import base64
import time
import os
import tempfile
from gtts import gTTS
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="மொழி - Tamil Hindi Translator",
    page_icon="🗣️",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;700&family=Noto+Sans:wght@400;700&display=swap');

    .main-container {
        text-align: center;
        padding: 20px;
    }

    .app-logo {
        max-width: 140px;
        margin: 0 auto 10px auto;
        display: block;
        border-radius: 16px;
    }

    .app-title {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #FF6B35;
        margin: 0;
        line-height: 1.1;
        text-shadow: 0 2px 12px rgba(255,107,53,0.4);
        letter-spacing: 2px;
    }

    .creator-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFD700;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin: 4px 0 0 0;
    }

    .subtitle {
        font-size: 0.95rem;
        color: #8899BB;
        font-style: italic;
        margin: 2px 0 24px 0;
        letter-spacing: 1px;
    }

    .lang-card {
        background: #1E2130;
        border-radius: 16px;
        padding: 20px 24px;
        margin: 12px 0;
        border: 1px solid #2E3350;
        transition: border-color 0.3s;
    }

    .lang-card.active {
        border-color: #FF6B35;
        box-shadow: 0 0 16px rgba(255,107,53,0.2);
    }

    .lang-label {
        font-size: 0.8rem;
        color: #667799;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }

    .lang-text {
        font-size: 1.6rem;
        font-weight: 600;
        color: #EEEEFF;
        font-family: 'Noto Sans Tamil', 'Noto Sans', sans-serif;
        min-height: 44px;
        line-height: 1.4;
    }

    .status-bar {
        background: #1E2130;
        border-radius: 50px;
        padding: 12px 28px;
        display: inline-block;
        margin: 16px auto;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .status-listening { color: #00E5FF; }
    .status-processing { color: #FFD700; }
    .status-speaking { color: #69FF79; }
    .status-error { color: #FF4444; }

    .mic-hint {
        font-size: 0.85rem;
        color: #667799;
        margin-top: 8px;
    }

    .divider {
        border: none;
        border-top: 1px solid #2E3350;
        margin: 18px 0;
    }

    .history-item {
        background: #1A1E2E;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        text-align: left;
        border-left: 3px solid #FF6B35;
    }

    .history-dir {
        font-size: 0.75rem;
        color: #FF6B35;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }

    .history-original { color: #AABBDD; font-size: 1rem; }
    .history-translated { color: #FFFFFF; font-size: 1.05rem; font-weight: 600; }

    .stAudioInput > label { display: none; }

    div[data-testid="stVerticalBlock"] > div:has(.stAudioInput) {
        display: flex;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "status" not in st.session_state:
    st.session_state.status = "listening"
if "last_audio_key" not in st.session_state:
    st.session_state.last_audio_key = 0
if "auto_rerun" not in st.session_state:
    st.session_state.auto_rerun = False
if "tts_audio_b64" not in st.session_state:
    st.session_state.tts_audio_b64 = None
if "tts_duration" not in st.session_state:
    st.session_state.tts_duration = 3


def detect_and_transcribe(audio_bytes):
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
        for lang_code, lang_name in [("ta-IN", "Tamil"), ("hi-IN", "Hindi")]:
            try:
                text = recognizer.recognize_google(audio_data, language=lang_code)
                if text and len(text.strip()) > 0:
                    return text.strip(), lang_name
            except sr.UnknownValueError:
                continue
            except Exception:
                continue
        return None, None
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def translate_text(text, source_lang):
    try:
        if source_lang == "Tamil":
            translated = GoogleTranslator(source="ta", target="hi").translate(text)
            return translated, "Hindi"
        else:
            translated = GoogleTranslator(source="hi", target="ta").translate(text)
            return translated, "Tamil"
    except Exception as e:
        return None, None


def generate_tts(text, target_lang):
    lang_code = "hi" if target_lang == "Hindi" else "ta"
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_bytes = buf.read()
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        duration = max(2, len(text) // 8)
        return b64, duration
    except Exception:
        return None, 3


logo_path = "logo.png"
st.markdown('<div class="main-container">', unsafe_allow_html=True)

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(
        f'<img src="data:image/png;base64,{logo_b64}" class="app-logo" alt="Logo">',
        unsafe_allow_html=True
    )
else:
    st.markdown('<div style="font-size:3rem;margin-bottom:8px;">🗣️</div>', unsafe_allow_html=True)

st.markdown('<p class="app-title">மொழி</p>', unsafe_allow_html=True)
st.markdown('<p class="creator-name">EASWAR</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Created by இங்</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="lang-card"><div class="lang-label">🇮🇳 Tamil Input / Output</div><div style="font-size:0.95rem;color:#667799;">தமிழ் ↔ हिंदी</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="lang-card"><div class="lang-label">🇮🇳 Hindi Input / Output</div><div style="font-size:0.95rem;color:#667799;">हिंदी ↔ தமிழ்</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

if st.session_state.tts_audio_b64 and st.session_state.auto_rerun:
    dur_ms = st.session_state.tts_duration * 1000 + 800
    st.markdown(
        f"""
        <script>
        setTimeout(function() {{
            const buttons = window.parent.document.querySelectorAll('button');
            buttons.forEach(btn => {{
                if(btn.innerText.includes('rerun') || btn.getAttribute('data-testid') === 'stBaseButton-secondary') {{
                    btn.click();
                }}
            }});
            window.parent.location.reload();
        }}, {dur_ms});
        </script>
        """,
        unsafe_allow_html=True
    )

if st.session_state.tts_audio_b64:
    audio_b64 = st.session_state.tts_audio_b64
    st.markdown(
        f"""
        <audio autoplay style="display:none;" id="tts-audio">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )

status = st.session_state.status
if status == "listening":
    status_html = '<div class="status-bar"><span class="status-listening">🎙️ Listening... Speak Tamil or Hindi</span></div>'
elif status == "processing":
    status_html = '<div class="status-bar"><span class="status-processing">⚙️ Translating...</span></div>'
elif status == "speaking":
    status_html = '<div class="status-bar"><span class="status-speaking">🔊 Speaking Translation...</span></div>'
else:
    status_html = '<div class="status-bar"><span class="status-error">❌ Could not detect speech. Try again.</span></div>'

st.markdown(f'<div style="text-align:center">{status_html}</div>', unsafe_allow_html=True)

if st.session_state.auto_rerun:
    st.session_state.auto_rerun = False
    st.session_state.tts_audio_b64 = None
    st.session_state.status = "listening"
    time.sleep(st.session_state.tts_duration + 0.5)
    st.rerun()

audio_key = f"audio_input_{st.session_state.last_audio_key}"
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
audio_value = st.audio_input("Record your voice", key=audio_key)
st.markdown('<p class="mic-hint">Press the mic button, speak in Tamil or Hindi, then stop recording</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if audio_value is not None:
    audio_bytes = audio_value.read()
    if len(audio_bytes) > 1000:
        st.session_state.status = "processing"

        with st.spinner(""):
            recognized_text, source_lang = detect_and_transcribe(audio_bytes)

        if recognized_text and source_lang:
            translated_text, target_lang = translate_text(recognized_text, source_lang)

            if translated_text:
                tts_b64, dur = generate_tts(translated_text, target_lang)

                st.session_state.tts_audio_b64 = tts_b64
                st.session_state.tts_duration = dur
                st.session_state.status = "speaking"
                st.session_state.auto_rerun = True
                st.session_state.last_audio_key += 1

                st.session_state.history.insert(0, {
                    "direction": f"{source_lang} → {target_lang}",
                    "original": recognized_text,
                    "translated": translated_text,
                })
                if len(st.session_state.history) > 10:
                    st.session_state.history = st.session_state.history[:10]

                st.rerun()
            else:
                st.session_state.status = "error"
                st.session_state.last_audio_key += 1
                st.rerun()
        else:
            st.session_state.status = "error"
            st.session_state.last_audio_key += 1
            st.rerun()

if st.session_state.history:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem;color:#667799;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">Recent Translations</div>', unsafe_allow_html=True)

    for item in st.session_state.history[:5]:
        st.markdown(
            f"""
            <div class="history-item">
                <div class="history-dir">{item['direction']}</div>
                <div class="history-original">{item['original']}</div>
                <div class="history-translated">→ {item['translated']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()
with col_b:
    if st.button("🔄 Reset Mic", use_container_width=True):
        st.session_state.last_audio_key += 1
        st.session_state.status = "listening"
        st.session_state.tts_audio_b64 = None
        st.session_state.auto_rerun = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;font-size:0.75rem;color:#445566;">மொழி — Bilingual Tamil ↔ Hindi Voice Translator</div>', unsafe_allow_html=True)
