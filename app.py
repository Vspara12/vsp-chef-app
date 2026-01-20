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

# 3. Smart Model Selection (இது அப்படியே இருக்கட்டும், இதுதான் Error வராமல் பார்த்துக் கொள்கிறது)
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
            st.success(f"✅ VSP Chef is Connected! (Using: {chosen_model})")
        except:
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
    txt = st.text_area("What ingredients do you have? (You can type in ANY language)")
    if st.button("Get Recipe"):
        user_query = txt

with tab2:
    file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
    if file and st.button("Analyze & Cook"):
        user_img = Image.open(file)
        user_query = "Suggest a world-class recipe based on these items."

# 5. Cooking Logic (UNIVERSAL LANGUAGE UPDATE)
if user_query and model:
    with st.spinner("VSP Chef is cooking..."):
        try:
            # --- புதிய கட்டளை (Prompt) ---
            # இது பயனர் பேசும் மொழியைத் தானாகவே கண்டுபிடிக்கும்.
            prompt = f"""
            You are VSP Chef, a world-renowned Master of World Cuisine.
            
            USER INPUT: "{user_query}"
            
            STRICT INSTRUCTIONS:
            1. DETECT the language used by the user in the input above.
            2. REPLY IN THE EXACT SAME LANGUAGE as the user. 
               (Example: If input is Tamil -> Reply in Tamil. If French -> Reply in French. If Hindi -> Reply in Hindi).
            3. Suggest a delicious world-class recipe based on the ingredients provided.
            4. Provide clear, step-by-step cooking instructions.
            5. Be professional, friendly, and encouraging.
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
