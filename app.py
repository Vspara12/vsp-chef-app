import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI STYLING (உங்கள் டிசைன்) ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    div[data-testid="column"] {display: flex; justify_content: center;}
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

# 3. API SETUP (Direct & Strict)
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key Missing. Please check Environment Variables.")
    st.stop()

# Clean Key
clean_key = api_key.strip().replace('"', '').replace("'", "")
genai.configure(api_key=clean_key)

# --- THE FIX: ONLY USE 1.5 FLASH ---
# பழைய மாடல்களை (gemini-pro) நீக்கிவிட்டோம்.
# இது மட்டும்தான் இப்போது வேலை செய்யும்.
model = genai.GenerativeModel("gemini-1.5-flash")

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
                # இப்போது உண்மையான பிழை என்னவென்று நமக்குத் தெரியும்
                err_msg = str(e)
                if "429" in err_msg:
                    st.warning("👨‍🍳 Chef is busy (Quota Limit). Please wait 1 minute.")
                elif "404" in err_msg:
                    st.error(f"Error: Model not found. (Server needs update). Details: {e}")
                else:
                    st.error(f"Unexpected Error: {e}")
