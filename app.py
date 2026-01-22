import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI CSS ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    div[data-testid="column"] {display: flex; justify_content: center;}
    h1 {text-align: center; margin-top: -20px; color: #333;}
    h3 {text-align: center; color: #E67E22; font-size: 1rem; text-transform: uppercase;}
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("myphoto.png"): st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"): st.image("myphoto.jpg", width=130)

st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 3. API SETUP
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# 4. MASTER FUNCTION (எந்தப் பெயர் வேலை செய்கிறதோ அதை எடுக்கும்)
def get_chef_response(prompt_text, image_input=None):
    # முயற்சி செய்ய வேண்டிய பெயர்களின் பட்டியல் (Priority Order)
    # ஐரோப்பாவில் சில சமயம் குறிப்பிட்ட பெயர்கள் மட்டுமே வேலை செய்யும்
    model_names = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-pro",
        "models/gemini-1.5-pro",
        "gemini-pro"
    ]
    
    clean_key = api_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_key)
    
    last_error = None

    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            
            # சமைக்க முயற்சி செய் (Generate)
            if image_input:
                # பழைய pro மாடல் படத்தை ஏற்காது
                if "1.5" not in name and "flash" not in name:
                    response = model.generate_content(prompt_text)
                else:
                    response = model.generate_content([prompt_text, image_input])
            else:
                response = model.generate_content(prompt_text)
            
            return response # வெற்றி! (இங்கே லூப் நின்றுவிடும்)
            
        except Exception as e:
            # தோல்வி என்றால் அடுத்த பெயரை முயற்சிக்கும்
            last_error = e
            continue 
            
    # எல்லாப் பெயர்களும் தோல்வியடைந்தால் மட்டும் பிழை
    raise last_error

# 5. Refresh Button
if 'generated' not in st.session_state: st.session_state.generated = False
if st.session_state.generated:
    if st.button("🔄 Start New Recipe"):
        st.session_state.generated = False
        st.rerun()

# 6. Inputs
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

    # 7. Execution
    if user_query:
        if not api_key:
            st.error("API Key Missing")
        else:
            with st.spinner("VSP Chef is cooking..."):
                try:
                    prompt = f"""
                    You are VSP Chef. 
                    USER INPUT: "{user_query}"
                    RULES: Reply in the user's language. Suggest a delicious recipe.
                    """
                    
                    # நமது புதிய 'Master Function'-ஐ அழைக்கிறோம்
                    response = get_chef_response(prompt, user_img)
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    st.balloons()
                    st.session_state.generated = True
                    
                except Exception as e:
                    if "429" in str(e):
                        st.warning("👨‍🍳 Chef is busy! Please wait 30 seconds.")
                    else:
                        st.error(f"Connection Error: {e}")
