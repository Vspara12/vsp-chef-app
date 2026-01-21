import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Config
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- CSS FOR PERFECT UI (டிசைன் சரிசெய்யும் கோட்) ---
st.markdown("""
    <style>
    /* 1. தேவையில்லாத மேல் இடைவெளியை நீக்க */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* 2. லோகோவைச் சரியாக நடுவில் கொண்டு வர */
    div[data-testid="stImage"] {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
    }
    div[data-testid="stImage"] > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 3. VSP Chef தலைப்பு */
    h1 {
        text-align: center;
        margin-bottom: -20px !important; /* இடைவெளியை குறைக்க */
        padding-bottom: 0px !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    /* 4. MASTER OF WORLD CUISINE (கலர் மாற்றம் & இடைவெளி நீக்கம்) */
    h3 {
        text-align: center;
        margin-top: 0px !important;
        padding-top: 5px !important;
        color: #D35400 !important; /* அழகான ஆரஞ்சு நிறம் */
        font-size: 1rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase;
    }
    
    /* 5. பட்டன்கள் மற்றும் தேவையற்றவற்றை மறைக்க */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Display Logo (Center)
# மூன்று காலம்களுக்குப் பதில், ஒரே காலமில் வைத்து CSS மூலம் நடுவில் கொண்டு வருகிறோம்
if os.path.exists("myphoto.png"):
    st.image("myphoto.png", width=140)
elif os.path.exists("myphoto.jpg"):
    st.image("myphoto.jpg", width=140)

# 3. Titles (இடைவெளி இல்லாமல்)
st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 4. API & Model Setup
model = None
api_key = None
if "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if api_key:
    try:
        clean_key = api_key.strip().replace('\n', '').replace('\r', '').replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            chosen_model = next((m for m in available_models if 'flash' in m), None)
            if not chosen_model:
                chosen_model = next((m for m in available_models if 'pro' in m), 'gemini-pro')
            model = genai.GenerativeModel(chosen_model)
        except:
            model = genai.GenerativeModel('gemini-pro')
    except:
        st.error("API Error")

# 5. RESTART BUTTON LOGIC (இதுதான் முக்கியம்)
if 'generated' not in st.session_state:
    st.session_state.generated = False

# சமையல் வந்த பிறகு மட்டும் இந்த பட்டன் தெரியும்
if st.session_state.generated:
    if st.button("🔄 Start New Recipe (Refresh)"):
        st.session_state.generated = False
        st.rerun()

# 6. Inputs
tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
user_query = ""
user_img = None

with tab1:
    txt = st.text_area("What ingredients do you have? (Any language)", key="txt_input")
    if st.button("Get Recipe"):
        user_query = txt

with tab2:
    file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'], key="img_input")
    image_text = st.text_input("Add instructions (Optional):", placeholder="Ex: Make it spicy...", key="img_txt")
    if file and st.button("Analyze & Cook"):
        user_img = Image.open(file)
        if image_text:
            user_query = image_text
        else:
            user_query = "Identify ingredients and suggest a world-class recipe."

# 7. Cooking Logic
if user_query and model:
    with st.spinner("VSP Chef is cooking..."):
        try:
            prompt = f"""
            You are VSP Chef, a world-renowned Master of World Cuisine.
            USER INPUT: "{user_query}"
            
            CRITICAL LANGUAGE RULES:
            1. If user asks in Tamil -> Reply in TAMIL.
            2. If user asks in English -> Reply in ENGLISH.
            3. Detect and match the user's language automatically.
            
            COOKING INSTRUCTIONS:
            Suggest a delicious recipe with step-by-step instructions.
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
            
            # சமையல் முடிந்ததும் Refresh பட்டன் வர இது உதவும்
            st.session_state.generated = True
            
        except Exception as e:
            st.error(f"Error: {e}")
