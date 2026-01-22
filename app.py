import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI STYLING ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    h1 {text-align: center; margin-top: -20px; color: #333;}
    h3 {text-align: center; color: #E67E22; font-size: 1rem; text-transform: uppercase;}
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

# --- 🔍 DEBUGGING: VERSION CHECK (இதைச் சோதிக்க சேர்க்கப்பட்டுள்ளது) ---
# இது திரையில் வெர்ஷனைக் காட்டும். 0.8.3 வந்தால் வெற்றி!
# st.caption(f"System Version: {genai.__version__}") 

# 3. API & MODEL SETUP (The Final Fix)
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None

if api_key:
    try:
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        
        # நீங்கள் சொன்னது போல 1.5 Pro அல்லது Flash-ஐ நேரடியாக அழைக்கிறோம்
        # பழைய வெர்ஷனில் இது வேலை செய்யாது, புதியதில் கண்டிப்பாக வேலை செய்யும்.
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        
    except Exception as e:
        st.error(f"Setup Error: {e}")

# 4. Refresh Button
if 'generated' not in st.session_state: st.session_state.generated = False
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
        img = st.file_uploader("Upload fridge photo", type=['jpg','png','jpeg'])
        txt_img = st.text_input("Add instructions (Optional):")
        if img and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(img)
            user_query = txt_img if txt_img else "Recipe from this image"

    # 6. Execution
    if user_query:
        if not model:
            st.error("Connection Error: Please check API Key.")
        else:
            with st.spinner("VSP Chef is cooking..."):
                try:
                    prompt = f"""
                    You are VSP Chef. USER INPUT: "{user_query}"
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
                    # 429 என்றால் Quota, 404 என்றால் Version பிரச்சனை
                    if "429" in str(e):
                        st.warning("👨‍🍳 Chef is busy! (Quota limit). Wait 30s.")
                    elif "404" in str(e):
                        st.error(f"Version Error: Server is using old software ({genai.__version__}). Need >0.8.3")
                    else:
                        st.error(f"Error: {e}")
