import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. பக்க வடிவமைப்பு (Page Config)
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# 2. தேவையற்ற மெனுக்களை மறைத்தல் (Settings மாற்ற முடியாதபடி)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. தலைப்பு (Branding)
st.title("👨‍🍳 VSP Chef")
st.subheader("MASTER OF WORLD CUISINE 🌎")
st.write("Upload ingredients or a photo. I will suggest a world-class recipe!")

# 4. API Key அமைத்தல் (இதை பிறகு Secrets-ல் சேர்ப்போம்)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 5. VSP Chef அறிவுரைகள் (System Prompt)
    system_prompt = """
    You are 'VSP Chef', a world-renowned 'Master of World Cuisine'.
    You are NOT limited to Indian cooking. You are an expert in Italian, Mexican, Chinese, Thai, Indian, Continental, and all global cuisines.
    
    YOUR GOAL:
    Take the ingredients list or the photo provided by the user and suggest the BEST recipe from ANY cuisine that fits well.
    
    INSTRUCTIONS:
    1. Introduce yourself as "VSP Chef".
    2. Suggest a creative recipe name and its origin (e.g., "Mexican Tacos", "Italian Pasta").
    3. List the ingredients clearly.
    4. Provide step-by-step cooking instructions in ENGLISH.
    5. Be professional, classy, and encouraging like a Master Chef.
    """

    # 6. உள்ளீடுகள் (Inputs)
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_input = ""
    image_input = None
    submit = False

    with tab1:
        text_val = st.text_area("List your ingredients here (e.g., Chicken, Cheese, Tomato):")
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
            with st.spinner("VSP Chef is cooking up a masterpiece... 🍲"):
                try:
                    if image_input:
                        response = model.generate_content([system_prompt, user_input, image_input])
                    else:
                        response = model.generate_content([system_prompt, user_input])
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    st.success("Enjoy your culinary journey! - VSP Chef")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter ingredients or upload a photo.")
else:
    st.warning("Please add the GEMINI_API_KEY to your Streamlit Secrets.")
