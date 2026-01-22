import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- UI CSS (சுத்தமான மற்றும் அழகான டிசைன்) ---
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; padding-bottom: 3rem !important;}
    div[data-testid="column"] {display: flex; align-items: center; justify_content: center;}
    h1 {text-align: center; margin-top: -15px !important; margin-bottom: -10px !important; font-size: 2.2rem !important; font-weight: 800 !important;}
    h3 {text-align: center; color: #E67E22 !important; font-size: 1rem; font-weight: 600; text-transform: uppercase;}
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
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

# 3. SMART MODEL RESOLVER (இதுதான் 404 பிழையைத் தீர்க்கும் மருந்து)
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
model = None

if api_key:
    try:
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        
        # கூகுள் சர்வரிடம் உள்ள அனைத்து மாடல்களையும் தேடுகிறோம்
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 1. முதலில் 'flash' இருக்கிறதா பார்
            chosen_name = next((m for m in available_models if 'flash' in m), None)
            
            # 2. இல்லை என்றால் 'pro' இருக்கிறதா பார்
            if not chosen_name:
                chosen_name = next((m for m in available_models if 'pro' in m), None)
            
            # 3. அதுவும் இல்லை என்றால் பட்டியலில் உள்ள முதலாவது மாடல்
            if not chosen_name and available_models:
                chosen_name = available_models[0]
                
            if chosen_name:
                model = genai.GenerativeModel(chosen_name)
                # சோதனையில் வெற்றி பெற்றால் மட்டும் ஒரு சிறிய மெசேஜ்
                st.caption(f"Connected Successfully")
        except:
            # ஒருவேளை பட்டியல் எடுக்க முடியாவிட்டால், ஒரு பொதுவான பெயரை முயற்சிக்கும்
            model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"API Error: {e}")

# 4. RESTART BUTTON
if 'generated' not in st.session_state: st.session_state.generated = False
if st.session_state.generated:
    if st.button("🔄 Start New Recipe (Refresh)"):
        st.session_state.generated = False
        st.rerun()

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
        file = st.file_uploader("Upload photo", type=['jpg', 'png', 'jpeg'])
        image_text = st.text_input("Add instructions (Optional):")
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Identify ingredients and suggest a world-class recipe."

    # 6. COOKING LOGIC
    if user_query and model:
        with st.spinner("VSP Chef is cooking..."):
            try:
                prompt = f"""
                You are VSP Chef, Master of World Cuisine. 
                USER INPUT: "{user_query}"
                RULES: Reply in the USER'S LANGUAGE. Provide a delicious recipe with instructions.
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
                if "429" in str(e):
                    st.warning("👨‍🍳 Chef is busy! Please wait 1 minute. (Quota Limit reached)")
                else:
                    st.error(f"Cooking Error: {e}")
