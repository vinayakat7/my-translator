import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import io

# 1. பக்காவான டிசைன் (நீங்கள் கேட்ட அதே ஸ்டைல்)
st.set_page_config(page_title="மொழி - Translator", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FF6B35;'>மொழி</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FFD700; letter-spacing: 5px;'>EASWAR</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8899BB;'>Tamil ↔ Hindi Voice Translator</p>", unsafe_allow_html=True)

st.divider()

# 2. முக்கியமான மைக் (இது 30 செகண்ட் வரை கட் ஆகாமல் கேட்கும்)
# மைக் பட்டனை அழுத்திப் பேசிவிட்டு, மீண்டும் அழுத்தினால் அது அப்படியே சேமிக்கும்
audio_value = st.audio_input("மைக் பட்டனை அழுத்திப் பேசவும்")

if audio_value:
    st.audio(audio_value) # நீங்கள் பேசியதை நீங்களே கேட்கலாம்
    st.success("குரல் பதிவாகிவிட்டது! கீழே உள்ள பாக்ஸில் பேசி மொழிபெயர்க்கவும்.")

st.divider()

# 3. தமிழ் ↔ ஹிந்தி மொழிபெயர்ப்பு (Chat Input - இதில் மைக் மூலமும் பேசலாம்)
user_text = st.chat_input("இங்கே பேசவும் (Keyboard Mic பயன்படுத்தலாம்)...")

if user_text:
    # தானாகவே தமிழை ஹிந்தியாகவும், ஹிந்தியை தமிழாகவும் மாற்றும்
    translated = GoogleTranslator(source='auto', target='hi').translate(user_text)
    
    # ஒருவேளை ஏற்கனவே ஹிந்தியில் இருந்தால் தமிழுக்கு மாற்றும்
    if translated.lower() == user_text.lower():
        translated = GoogleTranslator(source='auto', target='ta').translate(user_text)
        target_lang = 'ta'
    else:
        target_lang = 'hi'
    
    # முடிவை திரையில் காட்ட
    st.markdown(f"### 📝 மொழிபெயர்ப்பு: {translated}")
    
    # 4. வாய்ஸ் அவுட்புட் (30 செகண்ட் வரை ஹிந்தியில் பேசும்)
    tts = gTTS(text=translated, lang=target_lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True) # தானாகவே மொழிபெயர்ப்பைச் சொல்லும்
            
