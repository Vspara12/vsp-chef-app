import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI CSS ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    h1 {text-align: center; margin-top: -15px !important; color: #1E1E1E !important;}
    h3 {text-align: center; color: #E67E22 !important; font-size: 0.9rem !important;}
    div[data-testid="column"] {display: flex; justify_content: center;}
    #MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=130)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# API Setup
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key Missing")
    st.stop()

# --- எளிய மாடல் தேர்வு (Simple Model Selection) ---
genai.configure(api_key=api_key)
# பழைய வெர்ஷனிலும் வேலை செய்யும் பொதுவான பெயர்
model = genai.GenerativeModel('gemini-pro') 

# Inputs
if 'generated' not in st.session_state: st.session_state.generated = False
if st.session_state.generated:
    if st.button("🔄 Start New Recipe"): 
        st.session_state.generated = False
        st.rerun()

if not st.session_state.generated:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Ingredients", "📷 Photo"])
    user_query = None
    user_img = None

    with tab1:
        txt = st.text_area("What do you have?", height=100)
        if st.button("Get Recipe", type="primary"): user_query = txt
    
    with tab2:
        img = st.file_uploader("Upload photo", type=['jpg','png','jpeg'])
        txt_img = st.text_input("Notes:")
        if img and st.button("Analyze", type="primary"):
            user_img = Image.open(img)
            user_query = txt_img if txt_img else "Recipe from this image"

    if user_query:
        with st.spinner("Cooking..."):
            try:
                prompt = f"Act as VSP Chef. Suggest a recipe for: {user_query}. Reply in user's language."
                if user_img:
                    # படங்களுக்கு மட்டும் 1.5 தேவை
                    flash_model = genai.GenerativeModel('gemini-1.5-flash')
                    response = flash_model.generate_content([prompt, user_img])
                else:
                    # எழுத்துக்கு சாதாரண Pro போதும் (இது 404 வராது)
                    response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                st.session_state.generated = True
            except Exception as e:
                st.error(f"Error: {e}")
