import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- 🛑 FINAL ATTEMPT TO REMOVE BADGE (பட்டையை அகற்றும் கடைசி முயற்சி) ---
hide_streamlit_style = """
            <style>
            /* 1. மெனு மற்றும் தலைப்பை மறைக்க */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* 2. அந்தச் சிவப்பு பட்டையை கண்டுபிடித்து மறைக்க (பல வழிகளில்) */
            [data-testid="stToolbar"] {display: none !important;}
            [data-testid="stDecoration"] {display: none !important;}
            [data-testid="stStatusWidget"] {display: none !important;}
            
            /* 3. குறிப்பாக Viewer Badge-ஐ குறிவைத்து மறைக்க */
            div[class*="viewerBadge"] {
                visibility: hidden !important;
                display: none !important;
                pointer-events: none !important;
                opacity: 0 !important;
            }
            
            /* 4. ஒருவேளை அது மறையவில்லை என்றால், அதை திரைக்கு வெளியே தள்ளிவிடுவோம் */
            .viewerBadge_container__1QSob {
                display: none !important;
            }
            
            /* 5. மொபைலில் பாதுகாப்பிற்காக */
            body > div:last-child {
                display: none !important;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# -----------------------------------------------------------------------

# 2. Profile Photo
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=150)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=150)

st.markdown("<h1 style='text-align: center;'>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #cc7a00;'>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. Smart Model Selection
model = None
if "GEMINI_API_KEY" in st.secrets:
    try:
        api_key = st.secrets["GEMINI_API_KEY"].replace('"', '').replace("'", "").strip()
        genai.configure(api_key=api_key)
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            chosen_model = next((m for m in available_models if 'flash' in m), None)
            if not chosen_model:
                chosen_model = next((m for m in available_models if 'pro' in m), available_models[0])
            model = genai.GenerativeModel(chosen_model)
        except:
            model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"Setup Error: {e}")
else:
    st.warning("⚠️ Waiting for API Key...")

# 4. Inputs
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

# 5. Cooking Logic
if user_query and model:
    with st.spinner("VSP Chef is cooking..."):
        try:
            prompt = f"""
            You are VSP Chef, a world-renowned Master of World Cuisine.
            
            USER INPUT/CONTEXT: "{user_query}"
            
            CRITICAL LANGUAGE RULES:
            1. If the user explicitly asks for a language (e.g., "in Tamil"), reply in THAT language.
            2. If no language is specified, reply in the SAME language the user typed.
            3. If the user sent only a photo (no text), reply in English by default.
            
            COOKING INSTRUCTIONS:
            1. Analyze the input.
            2. Suggest a creative, delicious recipe.
            3. Provide step-by-step instructions.
            """
            
            if user_img:
                try:
                    response = model.generate_content([prompt, user_img])
                except:
                    response = model.generate_content(prompt)
            else:
                response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            st.balloons()
            st.success("Bon Appétit! - VSP Chef")
        except Exception as e:
            st.error(f"Error: {e}")
