import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>""", unsafe_allow_html=True)

# 2. Profile Photo
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=150)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=150)

st.markdown("<h1 style='text-align: center;'>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #cc7a00;'>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. Smart Model Selection (இதுதான் முக்கிய மாற்றம்)
model = None

if "GEMINI_API_KEY" in st.secrets:
    try:
        # API Key Cleaning
        api_key = st.secrets["GEMINI_API_KEY"].replace('"', '').replace("'", "").strip()
        genai.configure(api_key=api_key)
        
        # --- ஆட்டோமேட்டிக் மாடல் தேர்வு ---
        # நாம் பெயரைச் சொல்ல மாட்டோம். கூகுளிடம் உள்ள முதல் மாடலை அதுவே எடுக்கும்.
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # முன்னுரிமை: Flash அல்லது Pro மாடல்
            chosen_model = next((m for m in available_models if 'flash' in m), None)
            if not chosen_model:
                chosen_model = next((m for m in available_models if 'pro' in m), available_models[0])
            
            model = genai.GenerativeModel(chosen_model)
            st.success(f"✅ VSP Chef is Connected! (Using: {chosen_model})")
            
        except Exception as e:
            # ஒருவேளை லிஸ்ட் எடுக்க முடியாவிட்டால், பழைய Pro மாடலை எடுக்கும்
            model = genai.GenerativeModel('gemini-pro')
            st.warning("⚠️ Using Standard Mode")

    except Exception as e:
        st.error(f"Setup Error: {e}")
else:
    st.warning("⚠️ Waiting for API Key...")

# 4. Inputs
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

# 5. Cooking Logic
if user_query and model:
    with st.spinner("VSP Chef is cooking..."):
        try:
            prompt = f"You are VSP Chef, Master of World Cuisine. The user has: {user_query}. Suggest a creative recipe. Reply in English with step-by-step instructions."
            
            if user_img:
                try:
                    response = model.generate_content([prompt, user_img])
                except:
                    st.warning("Info: This model might not support images directly, trying text only...")
                    response = model.generate_content(prompt)
            else:
                response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            st.balloons()
            st.success("Bon Appétit! - VSP Chef")
        except Exception as e:
            st.error(f"Error: {e}")
