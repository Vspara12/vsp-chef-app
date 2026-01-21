import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Config
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- CSS FOR PERFECT UI ---
st.markdown("""
    <style>
    /* Mobile Spacing Fix */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* Logo Centering */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify_content: center;
    }
    
    /* VSP Chef Title */
    h1 {
        text-align: center;
        margin-top: -15px !important;
        margin-bottom: -10px !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #1E1E1E !important;
    }
    
    /* MASTER Title (Orange) */
    h3 {
        text-align: center;
        margin-top: 0px !important;
        padding-top: 5px !important;
        color: #E67E22 !important; /* ஆரஞ்சு நிறம் */
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase;
    }
    
    /* Hide Buttons */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Display Logo (Centered)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=130)

# 3. Titles
st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 4. RESTART BUTTON (Refresh Logic)
if 'generated' not in st.session_state:
    st.session_state.generated = False

if st.session_state.generated:
    if st.button("🔄 Start New Recipe (Click here to Clear)"):
        st.session_state.generated = False
        st.rerun()

# 5. API & Model Logic (QUOTA SAVER MODE)
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
        
        # --- மாற்றம்: லிஸ்ட் எடுக்க வேண்டாம் (Quota மிச்சம்) ---
        # நேரடியாக Flash மாடலை அழைக்கிறோம்.
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            # அது இல்லையென்றால் பழைய Pro மாடல்
            model = genai.GenerativeModel('gemini-pro')
    except:
        st.error("Connection Issue")

# 6. Inputs
if not st.session_state.generated:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_query = ""
    user_img = None

    with tab1:
        txt = st.text_area("What ingredients do you have? (Any language)")
        if st.button("Get Recipe", type="primary"):
            user_query = txt

    with tab2:
        file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
        image_text = st.text_input("Add instructions (Optional):", placeholder="Ex: Make it spicy...")
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Identify ingredients and suggest a world-class recipe."

# 7. Cooking Logic
if 'user_query' in locals() and user_query and model:
    with st.spinner("VSP Chef is cooking..."):
        try:
            prompt = f"""
            You are VSP Chef, a world-renowned Master of World Cuisine.
            USER INPUT: "{user_query}"
            
            RULES:
            1. Reply in the USER'S LANGUAGE.
            2. Suggest a creative, delicious recipe.
            3. Provide step-by-step instructions.
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
            st.session_state.generated = True
            
        except Exception as e:
            # 429 Error வந்தால் அழகாகச் சொல்வோம்
            if "429" in str(e):
                st.warning("👨‍🍳 VSP Chef is very popular right now! Please wait 1 minute and try again. (Quota Limit Reached)")
            else:
                st.error(f"Error: {e}")
