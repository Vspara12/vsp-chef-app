import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- 🎨 PREMIUM UI CSS ---
st.markdown("""
    <style>
    /* 1. மொபைல் ஸ்கிரீன் இடைவெளியை மிகச்சரியாகக் குறைத்தல் */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 500px;
    }
    
    /* 2. லோகோ மற்றும் படங்களை நடுவில் கொண்டு வருதல் */
    div[data-testid="stImage"] > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 50%;
    }
    
    /* 3. VSP Chef தலைப்பு - மிகவும் கச்சிதமான இடைவெளி */
    h1 {
        text-align: center;
        margin-top: -10px !important;
        margin-bottom: 0px !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
    }
    
    /* 4. MASTER OF WORLD CUISINE - நிறம் மற்றும் அளவு */
    h3 {
        text-align: center;
        margin-top: 0px !important;
        padding-top: 0px !important;
        color: #E67E22 !important; /* Premium Orange */
        font-size: 0.9rem !important;
        font-weight: 600;
        letter-spacing: 1px;
    }

    /* 5. தேவையற்ற Streamlit பட்டன்களை முழுமையாக மறைத்தல் */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    
    /* 6. Tabs மற்றும் Inputs-கான சிறிய அலங்காரம் */
    .stTextArea textarea { border-radius: 10px; }
    .stButton button { width: 100%; border-radius: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. APP LOGIC & SESSION STATE
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'recipe_text' not in st.session_state:
    st.session_state.recipe_text = ""

# 3. DISPLAY LOGO & TITLES (சரியாக நடுவில்)
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=105)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=105)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 4. API & MODEL SETUP
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None

if api_key:
    try:
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        # Automatic Model Selection
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_name = next((m for m in available_models if 'flash' in m), available_models[0])
        model = genai.GenerativeModel(chosen_name)
    except: pass

# --- 5. INTERFACE LOGIC (மாற்றங்கள் இங்கேதான் உள்ளன) ---

# சமையல் குறிப்பு வந்த பிறகு, இந்த 'Restart' பட்டன் மட்டுமே தெரியும்
if st.session_state.generated:
    st.markdown("---")
    if st.button("🔄 Start New Recipe (Refresh)"):
        st.session_state.generated = False
        st.session_state.recipe_text = ""
        st.rerun()
    
    # காட்டப்படும் முடிவு (Result Display)
    st.markdown(st.session_state.recipe_text)
    st.balloons()
    st.success("Bon Appétit! - VSP Chef")

# சமையல் குறிப்பு வருவதற்கு முன்னால் மட்டும் இவை தெரியும்
else:
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_query = None
    user_img = None

    with tab1:
        txt = st.text_area("What's in your kitchen?", placeholder="Example: Tomato, Egg, Rice...", height=100)
        if st.button("Get Recipe", type="primary"): 
            user_query = txt

    with tab2:
        file = st.file_uploader("Upload photo", type=['jpg', 'png', 'jpeg'])
        image_text = st.text_input("Any special requests?", placeholder="Example: Make it spicy...")
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Suggest a world-class recipe based on this image."

    # 6. COOKING PROCESS
    if user_query and model:
        with st.spinner("VSP Chef is thinking..."):
            try:
                prompt = f"You are VSP Chef, Master of World Cuisine. USER INPUT: '{user_query}'. RULES: Reply in the USER'S LANGUAGE. Provide a delicious recipe with clear steps."
                if user_img: response = model.generate_content([prompt, user_img])
                else: response = model.generate_content(prompt)
                
                # விடையைச் சேமித்துவிட்டுப் பக்கத்தை மாற்றுகிறோம்
                st.session_state.recipe_text = response.text
                st.session_state.generated = True
                st.rerun()
            except Exception as e:
                if "429" in str(e): st.warning("Chef is busy! Please wait 1 minute.")
                else: st.error("Something went wrong. Please try again.")
