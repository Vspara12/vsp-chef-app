import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Config (Mobile Friendly)
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS FOR PERFECT MOBILE UI ---
st.markdown("""
    <style>
    /* 1. தேவையில்லாத இடைவெளிகளைக் குறைத்தல் */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 2. லோகோவைச் சிறிதாக்கி நடுவில் வைக்க */
    .profile-img-container {
        display: flex;
        justify_content: center;
        align_items: center;
        margin-bottom: 10px;
    }
    .profile-img {
        width: 100px;  /* லோகோ அளவு குறைக்கப்பட்டது */
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 3. தலைப்புகளைச் சிறிதாக்கி ஒரே வரியில் கொண்டு வர */
    h1 {
        font-size: 1.8rem !important;
        text-align: center;
        margin-bottom: 0px !important;
        margin-top: 0px !important;
    }
    h3 {
        font-size: 1rem !important;
        text-align: center;
        color: #cc7a00;
        margin-top: 5px !important;
        white-space: nowrap; /* ஒரே வரியில் வரவைக்க */
    }
    
    /* 4. மறைக்க வேண்டியவை */
    #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton {
        display: none !important;
    }
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Display Logo (Center & Small)
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=120) # அளவு 120px ஆக குறைக்கப்பட்டது
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=120)

# 3. Titles (Compact)
st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 4. API Key Logic
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None

if api_key:
    try:
        clean_key = api_key.strip().replace('\n', '').replace('\r', '').replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        try:
            # Auto-select model logic
            all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            chosen_model = next((m for m in all_models if 'flash' in m), None) or \
                           next((m for m in all_models if 'pro' in m), 'gemini-pro')
            model = genai.GenerativeModel(chosen_model)
        except:
            model = genai.GenerativeModel('gemini-pro')
    except:
        st.error("API Error")

# 5. Inputs & Refresh Logic
if 'generated' not in st.session_state:
    st.session_state.generated = False

# Refresh Button (Clears everything)
if st.session_state.generated:
    if st.button("🔄 Start New Recipe (Refresh)"):
        st.session_state.generated = False
        st.rerun()

# Tabs
tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
user_query = ""
user_img = None

with tab1:
    # Key is added to clear text on refresh
    txt = st.text_area("Ingredients (Any language):", key="txt_input")
    if st.button("Get Recipe", type="primary"):
        user_query = txt

with tab2:
    file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'], key="img_input")
    image_text = st.text_input("Instructions (Optional):", placeholder="Ex: Make it spicy...", key="img_txt")
    if file and st.button("Analyze & Cook", type="primary"):
        user_img = Image.open(file)
        user_query = image_text if image_text else "Suggest a recipe based on this image."

# 6. Cooking Logic
if user_query and model:
    with st.spinner("VSP Chef is cooking..."):
        try:
            prompt = f"""
            You are VSP Chef. USER INPUT: "{user_query}"
            RULES: Reply in the USER'S LANGUAGE. Suggest a delicious recipe with steps.
            """
            
            if user_img:
                try: response = model.generate_content([prompt, user_img])
                except: response = model.generate_content(prompt)
            else:
                response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            st.balloons()
            st.success("Bon Appétit! - VSP Chef")
            
            # Mark as generated to show Refresh button next time
            st.session_state.generated = True
            
        except Exception as e:
            st.error(f"Error: {e}")
