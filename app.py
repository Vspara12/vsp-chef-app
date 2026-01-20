import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. பக்க வடிவமைப்பு (Page Config)
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# 2. தேவையற்ற மெனுக்களை மறைத்தல் மற்றும் போட்டோ ஸ்டைல்
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .profile-pic {
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 50%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. உங்கள் புகைப்படத்தைக் காட்டுதல் (Centering the photo)
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=150)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=150)

# 4. தலைப்பு (Branding)
st.markdown("<h1 style='text-align: center;'>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #cc7a00;'>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload ingredients or a photo. I will suggest a world-class recipe!</p>", unsafe_allow_html=True)

# 5. API Key அமைத்தல்
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # VSP Chef அறிவுரைகள் (System Prompt)
    system_prompt = """
    You are 'VSP Chef', a world-renowned 'Master of World Cuisine'.
    You are an expert in all global cuisines (Italian, Mexican, Indian, etc.).
    Always introduce yourself as VSP Chef.
    Provide recipes in clear English with step-by-step instructions.
    """

    # 6. உள்ளீடுகள் (Inputs)
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_input = ""
    image_input = None
    submit = False

    with tab1:
        text_val = st.text_area("List your ingredients here:")
        if st.button("Ask VSP Chef (Text)"):
            user_input = text_val
            submit = True

    with tab2:
        uploaded_file = st.file_uploader("Upload a photo of your items", type=["jpg", "jpeg", "png"])
        if uploaded_file and st.button("Ask VSP Chef (Photo)"):
            image_input = Image.open(uploaded_file)
            user_input = "Identify ingredients and suggest a world-class recipe."
            submit = True

    # 7. விடை (Result)
    if submit:
        if user_input or image_input:
            with st.spinner("VSP Chef is creating a masterpiece... 🍲"):
                try:
                    if image_input:
                        response = model.generate_content([system_prompt, user_input, image_input])
                    else:
                        response = model.generate_content([system_prompt, user_input])
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    st.success("Bon Appétit! - VSP Chef")
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.warning("Please add the GEMINI_API_KEY to your Streamlit Secrets.")
