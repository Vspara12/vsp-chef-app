import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# Page config
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- Simple UI Style ---
st.markdown("""
<style>
.block-container {padding-top: 2rem;}
h1 {text-align: center;}
h3 {text-align: center; color: #E67E22;}
#MainMenu, footer, header {display: none;}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# --- API Key ---
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found. Set it in Secrets or Environment.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)

# Correct Models (New SDK)
model = genai.GenerativeModel("models/gemini-1.5-pro")
flash_model = genai.GenerativeModel("models/gemini-1.5-flash")

# Session state
if "generated" not in st.session_state:
    st.session_state.generated = False

if st.session_state.generated:
    if st.button("🔄 Start New Recipe"):
        st.session_state.generated = False
        st.rerun()

if not st.session_state.generated:

    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])

    user_query = None
    user_img = None

    # ---- Text Input ----
    with tab1:
        txt = st.text_area("What ingredients do you have? (Any language)", height=120)
        if st.button("Get Recipe", type="primary"):
            user_query = txt

    # ---- Image Input ----
    with tab2:
        img = st.file_uploader("Upload food photo", type=["jpg", "png", "jpeg"])
        note = st.text_input("Optional note:")
        if img and st.button("Analyze Photo", type="primary"):
            user_img = Image.open(img)
            user_query = note if note else "Create a recipe from this image"

    # ---- Generate Recipe ----
    if user_query:
        with st.spinner("👨‍🍳 Cooking..."):
            try:
                prompt = f"""
You are VSP Chef.
User input: {user_query}
Give a clear recipe with:
- Dish name
- Ingredients
- Steps
Reply in the same language as user.
"""

                if user_img:
                    response = flash_model.generate_content([prompt, user_img])
                else:
                    response = model.generate_content(prompt)

                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                st.session_state.generated = True

            except Exception as e:
                st.error(f"❌ Error: {e}")
