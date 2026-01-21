import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- HIDE ALL BADGES & LOGOS ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stToolbar"] {display: none !important;}
            [data-testid="stDecoration"] {display: none !important;}
            div[class*="viewerBadge"] {display: none !important;}
            .stDeployButton {display:none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 2. Profile Photo
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=150)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=150)

st.markdown("<h1 style='text-align: center;'>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #cc7a00;'>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. ROBUST API KEY HANDLING
api_key = None
if "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# 4. UNIVERSAL COOKING FUNCTION (பல மாடல்களை முயற்சிக்கும் மந்திரம்)
def try_generate_content(prompt, image=None):
    # முயற்சி செய்ய வேண்டிய மாடல்களின் பட்டியல்
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro',
        'gemini-pro',  # பழைய ஆனால் உறுதியான மாடல்
        'gemini-1.0-pro'
    ]
    
    last_error = None
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            if image:
                # சில பழைய மாடல்கள் படங்களை ஏற்காது, அதைத் தவிர்க்கிறோம்
                if 'pro' in model_name and '1.5' not in model_name: 
                     return model.generate_content(prompt) # படம் இல்லாமல் அனுப்பு
                return model.generate_content([prompt, image])
            else:
                return model.generate_content(prompt)
        except Exception as e:
            last_error = e
            continue # அடுத்த மாடலை முயற்சி செய்
            
    raise last_error # எதுவும் வேலை செய்யவில்லை என்றால் பிழையைக் காட்டு

# 5. CONFIG
if api_key:
    clean_key = api_key.strip().replace('\n', '').replace('\r', '').replace('"', '').replace("'", "")
    genai.configure(api_key=clean_key)
else:
    st.warning("⚠️ Connecting...")

# 6. Inputs
tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
user_query = ""
user_img = None

with tab1:
    txt = st.text_area("What ingredients do you have? (Any language)")
    if st.button("Get Recipe"):
        user_query = txt

with tab2:
    file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
    image_text = st.text_input("Add instructions (Optional):", placeholder="Ex: Make it spicy, or Reply in Tamil...")
    
    if file and st.button("Analyze & Cook"):
        user_img = Image.open(file)
        if image_text:
            user_query = image_text
        else:
            user_query = "Identify ingredients and suggest a world-class recipe."

# 7. Execution
if user_query:
    if not api_key:
        st.error("Connection Error: API Key missing.")
    else:
        with st.spinner("VSP Chef is cooking..."):
            try:
                # Prompt
                prompt = f"""
                You are VSP Chef, a world-renowned Master of World Cuisine.
                USER INPUT: "{user_query}"
                
                CRITICAL LANGUAGE RULES:
                1. If user asks in Tamil -> Reply in TAMIL.
                2. If user asks in English -> Reply in ENGLISH.
                3. If implied/mixed -> Detect and reply in the user's language.
                
                Provide a delicious recipe with step-by-step instructions.
                """
                
                # கால் செய்கிறோம் (எல்லா மாடல்களையும் முயற்சிக்கும்)
                response = try_generate_content(prompt, user_img)
                
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                st.success("Bon Appétit! - VSP Chef")
                
            except Exception as e:
                st.error(f"Sorry, I am busy right now. Please try again. (Error: {e})")
