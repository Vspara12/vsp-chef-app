import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- CSS TO HIDE BADGES & UI CLEANUP ---
hide_styles = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    .stDeployButton {display:none !important;}
    
    /* VSP Chef Styling */
    h1 {text-align: center; margin-top: -20px; color: #333;}
    h3 {text-align: center; color: #E67E22; font-size: 1rem;}
    </style>
"""
st.markdown(hide_styles, unsafe_allow_html=True)

# 2. Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=130)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. INTELLIGENT MODEL SCANNER (இதுதான் பிரச்சனைக்கான தீர்வு)
model = None
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        # Clean Key
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        
        # --- ஸ்கேனிங் ஆரம்பம் ---
        try:
            # 1. கூகுளிடம் உள்ள எல்லா மாடல்களையும் பட்டியலிடு
            all_models = genai.list_models()
            
            # 2. அதில் 'generateContent' செய்யக்கூடியதை மட்டும் எடு
            valid_models = []
            for m in all_models:
                if 'generateContent' in m.supported_generation_methods:
                    valid_models.append(m.name)
            
            # 3. அதில் சிறந்ததை தேர்ந்தெடு (Flash -> Pro -> First Available)
            chosen_model_name = None
            
            # முதலில் 1.5 Flash இருக்கிறதா பார்
            for m in valid_models:
                if 'flash' in m and '1.5' in m:
                    chosen_model_name = m
                    break
            
            # இல்லையென்றால் Pro இருக்கிறதா பார்
            if not chosen_model_name:
                for m in valid_models:
                    if 'pro' in m and '1.5' in m:
                        chosen_model_name = m
                        break
            
            # அதுவும் இல்லையென்றால் பழைய Pro
            if not chosen_model_name:
                for m in valid_models:
                    if 'gemini-pro' in m:
                        chosen_model_name = m
                        break
            
            # அதுவும் இல்லையென்றால் பட்டியலில் உள்ள முதலாவது
            if not chosen_model_name and valid_models:
                chosen_model_name = valid_models[0]
            
            # மாடலை செட் செய்
            if chosen_model_name:
                model = genai.GenerativeModel(chosen_model_name)
                # (Optional: Debuggingக்காக திரையில் காட்டலாம், ஆனால் Clean Lookக்காக மறைத்துள்ளேன்)
                # st.caption(f"Connected to: {chosen_model_name}") 
            else:
                st.error("No valid models found in this region.")
                
        except Exception as e:
            st.error(f"Error scanning models: {e}")

    except Exception as e:
        st.error(f"API Key Error: {e}")
else:
    st.warning("⚠️ Connecting to VSP Kitchen...")

# 4. Inputs
if 'generated' not in st.session_state: st.session_state.generated = False
if st.session_state.generated:
    if st.button("🔄 Start New Recipe"): 
        st.session_state.generated = False
        st.rerun()

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

    # 5. Execution
    if user_query:
        if not model:
            st.error("Connection failed. Please check API Key or try again later.")
        else:
            with st.spinner("VSP Chef is cooking..."):
                try:
                    prompt = f"""
                    You are VSP Chef. 
                    USER INPUT: "{user_query}"
                    RULES: 
                    1. Reply in the user's language (Tamil if Tamil, English if English).
                    2. Suggest a delicious recipe.
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
                    st.error(f"Error: {e}")
