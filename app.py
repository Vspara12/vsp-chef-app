import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Config
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳")

# 2. Styles
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>""", unsafe_allow_html=True)

# 3. Profile Photo
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=150)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=150)

st.markdown("<h1 style='text-align: center;'>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #cc7a00;'>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 4. API Key & Model Configuration
if "GEMINI_API_KEY" in st.secrets:
    try:
        # API Key Cleaning
        api_key = st.secrets["GEMINI_API_KEY"].replace('"', '').replace("'", "").strip()
        genai.configure(api_key=api_key)
        
        # --- மிக முக்கியமான மாற்றம் ---
        # செல்லப்பெயர் வேண்டாம், நேரடி ID-யை பயன்படுத்துவோம்.
        # இது 100% வேலை செய்யும்.
        model = genai.GenerativeModel('gemini-1.5-flash-001')
        
        st.success("✅ VSP Chef is Connected!")
    except Exception as e:
        st.error(f"API Setup Error: {e}")
else:
    st.warning("⚠️ Waiting for API Key...")

# 5. UI
tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])

user_query = ""
user_img = None

with tab1:
    txt = st.text_area("What ingredients do you have?")
    if st.button("Get Recipe"):
        user_query = txt

with tab2:
    file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
    if file and st.button("Analyze & Cook"):
        user_img = Image.open(file)
        user_query = "Suggest a world-class recipe based on these items."

# 6. Response Logic
if user_query:
    with st.spinner("VSP Chef is cooking..."):
        try:
            # Prompt Setup
            prompt = f"You are VSP Chef, Master of World Cuisine. The user has: {user_query}. Suggest a creative recipe. Reply in English with step-by-step instructions."
            
            if user_img:
                response = model.generate_content([prompt, user_img])
            else:
                response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            st.balloons()
            st.success("Bon Appétit! - VSP Chef")
        except Exception as e:
            # ஒருவேளை இதுவும் வேலை செய்யவில்லை என்றால், பழைய மாடலுக்கு மாற்றுவோம்
            try:
                fallback_model = genai.GenerativeModel('gemini-pro')
                response = fallback_model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
                st.success("Bon Appétit! (Served by VSP Classic)")
            except:
                st.error(f"Error: {e}")
