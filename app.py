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
    div[data-testid="column"] {display: flex; justify_content: center;}
    
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
    if st.button("🔄 Start New Recipe"):
        st.session_state.generated = False
        st.rerun()

# 4. ROBUST FUNCTION (ஒன்று இல்லையென்றால் இன்னொன்று)
def generate_recipe(api_key, prompt, image=None):
    genai.configure(api_key=api_key)
    
    # வரிசையாக முயற்சிக்கும் பட்டியல்
    models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    last_error = None
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            if image:
                # பழைய pro மாடல் படத்தை ஏற்காது, எனவே எழுத்தை மட்டும் அனுப்புவோம்
                if 'gemini-pro' == model_name:
                    return model.generate_content(prompt)
                return model.generate_content([prompt, image])
            else:
                return model.generate_content(prompt)
        except Exception as e:
            last_error = e
            continue # அடுத்த மாடலை முயற்சி செய்
            
    raise last_error

# 5. INPUTS
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
            user_query = image_text if image_text else "Identify ingredients and suggest a recipe."

    # 6. EXECUTION
    if user_query:
        api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        
        if not api_key:
            st.error("API Key Missing")
        else:
            clean_key = api_key.strip().replace('"', '').replace("'", "")
            
            with st.spinner("VSP Chef is cooking..."):
                try:
                    prompt = f"""
                    You are VSP Chef.
                    USER INPUT: "{user_query}"
                    RULES: Reply in the user's language. Suggest a delicious recipe.
                    """
                    
                    response = generate_recipe(clean_key, prompt, user_img)
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    st.balloons()
                    st.session_state.generated = True
                    
                except Exception as e:
                    st.error(f"Something went wrong. Error: {e}")
