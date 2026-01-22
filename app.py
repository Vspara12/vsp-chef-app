import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- CLEAN UI ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    h1 {text-align: center; margin-top: -20px; color: #333;}
    h3 {text-align: center; color: #E67E22; font-size: 1rem;}
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=130)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# --- 🛑 DIAGNOSTIC CHECK (பிரச்சனையைத் தீர்க்கும் இடம்) ---
current_version = genai.__version__
# இது திரையில் வெர்ஷனைக் காட்டும்.
# இது 0.8.6 ஆக இருந்தால் மட்டுமே Flash வேலை செய்யும்.
st.info(f"System Check: AI Version {current_version}")

# 3. API SETUP
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    clean_key = api_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_key)
    
    # நாம் 1.5 Flash ஐ மட்டும் குறிவைப்போம்
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
    except:
        st.error("Model Setup Failed")
else:
    st.error("API Key Missing")

# 4. Inputs
if 'generated' not in st.session_state: st.session_state.generated = False
if st.session_state.generated:
    if st.button("🔄 Start New Recipe"):
        st.session_state.generated = False
        st.rerun()

if not st.session_state.generated:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_query = None
    user_img = None

    with tab1:
        txt = st.text_area("What ingredients do you have? (Any language)")
        if st.button("Get Recipe", type="primary"): user_query = txt
    
    with tab2:
        img = st.file_uploader("Upload fridge photo", type=['jpg','png','jpeg'])
        txt_img = st.text_input("Add instructions (Optional):")
        if img and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(img)
            user_query = txt_img if txt_img else "Recipe from this image"

    # 5. Execution
    if user_query:
        with st.spinner("VSP Chef is cooking..."):
            try:
                prompt = f"Act as VSP Chef. Suggest a recipe for: {user_query}. Reply in user's language."
                
                if user_img:
                    response = model.generate_content([prompt, user_img])
                else:
                    response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                st.session_state.generated = True
            except Exception as e:
                # இங்குதான் உண்மையான பிழையைப் பார்க்கிறோம்
                st.error(f"Error Details: {e}")
