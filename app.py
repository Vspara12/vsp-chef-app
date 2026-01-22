import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI STYLING (உங்கள் டிசைன்) ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    
    /* Logo Center */
    div[data-testid="column"] {display: flex; justify_content: center;}
    
    /* Title Styles */
    h1 {
        text-align: center; margin-top: -15px !important; margin-bottom: -10px !important;
        font-size: 2.2rem !important; font-weight: 800 !important; color: #1E1E1E !important;
    }
    h3 {
        text-align: center; margin-top: 0px !important; padding-top: 5px !important;
        color: #E67E22 !important; font-size: 0.9rem !important;
        font-weight: 600 !important; letter-spacing: 1.5px !important; text-transform: uppercase;
    }
    
    /* Hide Badges */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Display Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=130)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. API KEY SETUP
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# 4. ROBUST COOKING FUNCTION (1.5 Models Only)
def get_chef_response(user_input, image_input=None):
    # பழைய 'gemini-pro' ஐ நீக்கிவிட்டேன். இவை இரண்டும் தான் இப்போது சிறந்தது.
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    last_error = None
    
    # Key Configuration
    clean_key = api_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_key)

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            
            # Prompt Structure
            prompt = f"""
            You are VSP Chef, a world-renowned Master of World Cuisine.
            USER INPUT: "{user_input}"
            
            CRITICAL RULES:
            1. If user asks in Tamil -> Reply in TAMIL.
            2. If user asks in English -> Reply in ENGLISH.
            3. Detect and match the user's language automatically.
            
            INSTRUCTIONS:
            Suggest a delicious recipe with step-by-step instructions.
            """
            
            if image_input:
                response = model.generate_content([prompt, image_input])
            else:
                response = model.generate_content(prompt)
                
            return response # வெற்றி!
            
        except Exception as e:
            last_error = e
            continue # அடுத்த மாடலுக்குச் செல்
            
    raise last_error # இரண்டும் தோல்வியடைந்தால் மட்டும்

# 5. RESTART BUTTON
if 'generated' not in st.session_state: st.session_state.generated = False
if st.session_state.generated:
    if st.button("🔄 Start New Recipe"):
        st.session_state.generated = False
        st.rerun()

# 6. INPUTS
if not st.session_state.generated:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_query = None
    user_img = None

    with tab1:
        txt = st.text_area("What ingredients do you have? (Any language)")
        if st.button("Get Recipe", type="primary"): user_query = txt

    with tab2:
        file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
        image_text = st.text_input("Add instructions (Optional):", placeholder="Ex: Make it spicy...")
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Recipe from this image"

    # 7. EXECUTION
    if user_query:
        if not api_key:
            st.error("API Key Missing")
        else:
            with st.spinner("VSP Chef is cooking..."):
                try:
                    response = get_chef_response(user_query, user_img)
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    st.balloons()
                    st.session_state.generated = True
                    
                except Exception as e:
                    # Error Handling
                    err_msg = str(e)
                    if "429" in err_msg:
                        st.warning("👨‍🍳 Chef is busy! (Quota Exceeded). Please wait 30 seconds.")
                    elif "404" in err_msg:
                        st.error("Technical Error: Models not found. (Please check requirements.txt is updated)")
                    else:
                        st.error(f"Error: {e}")
