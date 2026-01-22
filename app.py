import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- CSS: HIDE EVERYTHING & MOBILE OPTIMIZED ---
hide_styles = """
    <style>
    /* Clean UI */
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    
    /* Logo Center */
    div[data-testid="column"] {display: flex; justify_content: center;}
    
    /* Hide ALL Streamlit Branding */
    #MainMenu, footer, header {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    .stDeployButton {display:none !important;}
    
    /* Titles */
    h1 {text-align: center; margin-top: -20px; color: #333;}
    h3 {text-align: center; color: #E67E22; font-size: 1rem; text-transform: uppercase;}
    </style>
"""
st.markdown(hide_styles, unsafe_allow_html=True)

# 2. Logo & Title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=130)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. API SETUP
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# 4. MAGIC FUNCTION: TRY MODELS ONE BY ONE
def get_recipe_from_any_model(prompt_text, image_input=None):
    # நாம் பயன்படுத்த வேண்டிய பாதுகாப்பான மாடல்கள் (Priority List)
    # 2.5 Pro-வை இதில் சேர்க்கவில்லை, ஏனெனில் அதுதான் Error தந்தது.
    models_list = [
        "gemini-1.5-flash",          # Best & Fast
        "gemini-1.5-flash-latest",   # Alternative
        "gemini-1.5-pro",            # High Quality
        "gemini-pro"                 # Old but Reliable
    ]
    
    last_exception = None
    
    # ஒவ்வொன்றாக முயற்சிக்கும்
    for model_name in models_list:
        try:
            model = genai.GenerativeModel(model_name)
            
            if image_input:
                # பழைய Pro மாடல் படங்களை ஏற்காது, அதைத் தவிர்க்கிறோம்
                if "1.5" not in model_name and "flash" not in model_name:
                    response = model.generate_content(prompt_text)
                else:
                    response = model.generate_content([prompt_text, image_input])
            else:
                response = model.generate_content(prompt_text)
                
            return response # வெற்றி! விடையை அனுப்பு
            
        except Exception as e:
            # தோல்வி என்றால் அடுத்ததை முயற்சிக்கும்
            last_exception = e
            continue
            
    # எதுவுமே வேலை செய்யவில்லை என்றால் மட்டும் Error
    raise last_exception

# 5. Inputs
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

    # 6. Execution
    if user_query:
        if not api_key:
            st.error("API Key Missing")
        else:
            # Clean Key
            clean_key = api_key.strip().replace('"', '').replace("'", "")
            genai.configure(api_key=clean_key)
            
            with st.spinner("VSP Chef is cooking..."):
                try:
                    prompt = f"""
                    You are VSP Chef. 
                    USER INPUT: "{user_query}"
                    RULES: 
                    1. Reply in the user's language.
                    2. Suggest a world-class recipe.
                    """
                    
                    # Call the Magic Function
                    response = get_recipe_from_any_model(prompt, user_img)
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    st.balloons()
                    st.session_state.generated = True
                    
                except Exception as e:
                    # 429 Error வந்தால் மட்டும் இதைக் காட்டு
                    if "429" in str(e):
                        st.warning("⏳ Chef is busy! Please wait 30 seconds and try again.")
                    else:
                        st.error(f"Something went wrong. (Error: {e})")
