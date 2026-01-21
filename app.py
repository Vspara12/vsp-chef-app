import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- HIDE ALL BADGES & LOGOS ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stToolbar"] {display: none !important;}
            [data-testid="stDecoration"] {display: none !important;}
            div[class*="viewerBadge"] {display: none !important;}
            .stDeployButton {display:none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 2. Profile Photo
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=150)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=150)

st.markdown("<h1 style='text-align: center;'>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #cc7a00;'>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. ROBUST API KEY & MODEL HANDLING
model = None
api_key = None

# Get API Key
if "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if api_key:
    try:
        # Clean Key
        clean_key = api_key.strip().replace('\n', '').replace('\r', '').replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        
        # --- SMART MODEL SELECTION (The Fix for 404) ---
        try:
            # 1. கூகுளிடம் உள்ள மாடல்களைப் பட்டியலிடு
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 2. அதில் 'flash' உள்ளதா எனத் தேடு
            chosen_model_name = next((m for m in available_models if 'flash' in m), None)
            
            # 3. இல்லை என்றால் 'pro' அல்லது முதலில் உள்ளதை எடு
            if not chosen_model_name:
                chosen_model_name = next((m for m in available_models if 'pro' in m), 'gemini-pro')
            
            model = genai.GenerativeModel(chosen_model_name)
            # st.success(f"Connected to {chosen_model_name}") # Testing only
            
        except Exception as e:
            # பட்டியலிட முடியாவிட்டால், பாதுகாப்பான பழைய மாடலை எடு
            model = genai.GenerativeModel('gemini-pro')

    except Exception as e:
        st.error(f"Config Error: {e}")
else:
    st.warning("⚠️ Connecting...")

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
if user_query:
    if not model:
        st.error("Checking connection... Please try again in 5 seconds.")
    else:
        with st.spinner("VSP Chef is cooking..."):
            try:
                prompt = f"""
                You are VSP Chef, a world-renowned Master of World Cuisine.
                
                USER INPUT/CONTEXT: "{user_query}"
                
                CRITICAL LANGUAGE RULES:
                1. If the user explicitly asks for a language (e.g., "in Tamil"), reply in THAT language.
                2. If no language is specified, reply in the SAME language the user typed.
                
                COOKING INSTRUCTIONS:
                1. Analyze the input.
                2. Suggest a creative, delicious recipe.
                3. Provide step-by-step instructions.
                """
                
                if user_img:
                    try:
                        response = model.generate_content([prompt, user_img])
                    except:
                        # If image fails, try text only
                        response = model.generate_content(prompt)
                else:
                    response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                st.success("Bon Appétit! - VSP Chef")
            except Exception as e:
                st.error(f"Recipe Error: {e}")
