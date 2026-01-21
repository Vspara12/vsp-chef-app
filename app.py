import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI STYLING (நீங்கள் கேட்ட டிசைன்) ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    div[data-testid="column"] {display: flex; align-items: center; justify_content: center;}
    
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

# 3. RESTART BUTTON
if 'generated' not in st.session_state: st.session_state.generated = False
if st.session_state.generated:
    if st.button("🔄 Start New Recipe (Click here to Clear)"):
        st.session_state.generated = False
        st.rerun()

# 4. ROBUST MODEL FUNCTION (சங்கிலித் தொடர் முயற்சி)
def get_gemini_response(api_key, prompt, image=None):
    # முயற்சி செய்ய வேண்டிய மாடல்களின் பட்டியல் (Priority Order)
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-1.0-pro"
    ]
    
    last_error = None
    genai.configure(api_key=api_key)

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            if image:
                # சில பழைய மாடல்கள் படங்களை ஏற்காது, அதைத் தவிர்க்கிறோம்
                if "1.5" not in model_name: 
                    return model.generate_content(prompt)
                return model.generate_content([prompt, image])
            else:
                return model.generate_content(prompt)
        except Exception as e:
            # பிழை வந்தால் அடுத்த மாடலுக்குத் தாவு
            last_error = e
            continue
            
    # எதுவுமே வேலை செய்யவில்லை என்றால் மட்டும் பிழை காட்டு
    raise last_error

# 5. INPUTS
if not st.session_state.generated:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_query = ""
    user_img = None

    with tab1:
        txt = st.text_area("What ingredients do you have? (Any language)")
        if st.button("Get Recipe", type="primary"): user_query = txt

    with tab2:
        file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
        image_text = st.text_input("Add instructions (Optional):", placeholder="Ex: Make it spicy...")
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Identify ingredients and suggest a world-class recipe."

# 6. EXECUTION
if 'user_query' in locals() and user_query:
    # Get Key
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("Technical Issue: API Key missing.")
    else:
        # Clean Key
        clean_key = api_key.strip().replace('\n', '').replace('\r', '').replace('"', '').replace("'", "")
        
        with st.spinner("VSP Chef is cooking (Trying best model)..."):
            try:
                prompt = f"""
                You are VSP Chef, a world-renowned Master of World Cuisine.
                USER INPUT: "{user_query}"
                RULES: Reply in the USER'S LANGUAGE. Suggest a delicious recipe with steps.
                """
                
                # கால் செய்கிறோம் (எல்லா மாடல்களையும் முயற்சிக்கும்)
                response = get_gemini_response(clean_key, prompt, user_img)
                
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                st.success("Bon Appétit! - VSP Chef")
                st.session_state.generated = True
                
            except Exception as e:
                if "429" in str(e):
                    st.warning("👨‍🍳 VSP Chef is busy! Please wait 1 minute. (Quota Limit)")
                else:
                    st.error(f"Error: {e}")
