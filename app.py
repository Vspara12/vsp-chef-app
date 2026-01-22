import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- 🎨 PREMIUM UI & CENTERING CSS ---
st.markdown("""
    <style>
    /* 1. மொபைல் திரை இடைவெளி குறைப்பு */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 500px;
    }
    
    /* 2. லோகோவை மிகச்சரியாக நடுவில் வைக்க */
    [data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    
    .centered-image {
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    img {
        border-radius: 15px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 3. தலைப்பு டிசைன் */
    h1 {
        text-align: center;
        margin-top: -10px !important;
        margin-bottom: 0px !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    h3 {
        text-align: center;
        margin-top: 0px !important;
        padding-top: 0px !important;
        color: #E67E22 !important; /* Premium Orange */
        font-size: 0.95rem !important;
        font-weight: 600;
        letter-spacing: 1px;
    }

    /* 4. Streamlit மறைக்கும் கோட் */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    
    /* 5. பட்டன் ஸ்டைல் */
    .stButton button {
        width: 100%;
        border-radius: 25px;
        font-weight: bold;
        background-color: #E67E22;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# 2. APP LOGIC
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = ""

# 3. DISPLAY LOGO (சரியாக நடுவில் வைக்க 3 காலம்கள்)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=120)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=120)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 4. API & MODEL SETUP
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None

if api_key:
    try:
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            chosen_name = next((m for m in available_models if 'flash' in m), available_models[0])
            model = genai.GenerativeModel(chosen_name)
        except:
            model = genai.GenerativeModel('gemini-1.5-flash')
    except: pass

# --- 5. INTERFACE LOGIC ---

if st.session_state.generated:
    st.markdown("---")
    if st.button("🔄 Start New Recipe (Refresh)"):
        st.session_state.generated = False
        st.session_state.recipe_result = ""
        st.rerun()
    
    st.markdown(st.session_state.recipe_result)
    st.balloons()
    st.success("Enjoy your cooking! - VSP Chef")

else:
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Take/Upload Photo"])
    user_query = ""
    user_img = None

    with tab1:
        txt = st.text_area("What ingredients do you have?", placeholder="Ex: Onion, Egg, Rice...", height=110)
        if st.button("Get Recipe", type="primary"): 
            user_query = txt

    with tab2:
        # இரண்டு வசதிகளையும் தருகிறோம்: கேமரா மற்றும் பைல் அப்லோட்
        img_source = st.radio("Choose source:", ["Camera 📸", "Upload from Gallery 📂"], horizontal=True)
        
        if img_source == "Camera 📸":
            file = st.camera_input("Take a photo of your ingredients")
        else:
            file = st.file_uploader("Choose a photo", type=['jpg', 'png', 'jpeg'])
            
        image_text = st.text_input("Any specific request?", placeholder="Example: Make it spicy...")
        
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Suggest a creative recipe based on this image."

    # 6. COOKING PROCESS
    if user_query and model:
        with st.spinner("VSP Chef is thinking..."):
            try:
                prompt = f"You are VSP Chef, Master of World Cuisine. USER INPUT: '{user_query}'. Suggest a delicious recipe. Reply in the USER'S LANGUAGE with clear steps."
                if user_img:
                    response = model.generate_content([prompt, user_img])
                else:
                    response = model.generate_content(prompt)
                
                st.session_state.recipe_result = response.text
                st.session_state.generated = True
                st.rerun()
                
            except Exception as e:
                if "429" in str(e): st.warning("Chef is busy! Please wait 30 seconds.")
                else: st.error("Technical issue. Please try again.")
