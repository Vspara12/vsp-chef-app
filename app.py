import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI STYLING (நீங்கள் கேட்ட டிசைன்) ---
st.markdown("""
    <style>
    /* Mobile Spacing */
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    
    /* Logo Center */
    div[data-testid="column"] {display: flex; justify_content: center;}
    
    /* Title Styles */
    h1 {
        text-align: center; margin-top: -15px !important; margin-bottom: -10px !important;
        font-size: 2.2rem !important; font-weight: 800 !important; color: #1E1E1E !important;
    }
    h3 {
        text-align: center; margin-top: 0px !important; padding-top: 5px !important;
        color: #E67E22 !important; font-size: 0.9rem !important;
        font-weight: 600 !important; letter-spacing: 1.5px !important; text-transform: uppercase;
    }
    
    /* Hide Badges */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Display Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=130)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. SIMPLE & STABLE API CONNECTION
# (சிக்கலான தேடுதல் வேண்டாம், நேரடியாக இணைக்கிறோம்)
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key Missing")
    st.stop()

# Clean Key
clean_key = api_key.strip().replace('"', '').replace("'", "")
genai.configure(api_key=clean_key)

# மாடல் தேர்வு (மிகவும் பாதுகாப்பான முறை)
# 'gemini-1.5-flash' என்பது இப்போது மிகச் சிறந்தது.
# அது வேலை செய்யவில்லை என்றால் 'gemini-pro' எடுக்கும்.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# 4. Refresh Button Logic
if 'generated' not in st.session_state:
    st.session_state.generated = False

if st.session_state.generated:
    if st.button("🔄 Start New Recipe"):
        st.session_state.generated = False
        st.rerun()

# 5. Inputs
if not st.session_state.generated:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_query = None
    user_img = None

    with tab1:
        txt = st.text_area("What ingredients do you have? (Any language)")
        if st.button("Get Recipe", type="primary"): user_query = txt

    with tab2:
        file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
        image_text = st.text_input("Add instructions (Optional):")
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Identify ingredients and suggest a recipe."

    # 6. Execution
    if user_query:
        with st.spinner("VSP Chef is cooking..."):
            try:
                prompt = f"""
                You are VSP Chef.
                USER INPUT: "{user_query}"
                RULES: Reply in the user's language. Suggest a delicious recipe.
                """
                
                if user_img:
                    response = model.generate_content([prompt, user_img])
                else:
                    response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                st.session_state.generated = True
                
            except Exception as e:
                st.error(f"Please try again. (Error: {e})")
