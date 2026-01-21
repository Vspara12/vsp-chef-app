import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Page Setup
st.set_page_config(page_title="VSP Chef", page_icon="👨‍🍳", layout="centered")

# --- CSS FOR PERFECT ALIGNMENT & DESIGN ---
st.markdown("""
    <style>
    /* 1. மொபைல் திரையில் மேல் இடைவெளியை முற்றிலுமாக நீக்குதல் */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* 2. லோகோவை வலுக்கட்டாயமாக நடுவில் கொண்டு வருதல் */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify_content: center;
    }
    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 50%; /* படத்தை வட்டமாக மாற்ற */
    }
    
    /* 3. VSP Chef தலைப்பு (இடைவெளி நீக்கப்பட்டது) */
    h1 {
        text-align: center;
        margin-top: -15px !important; /* லோகோவுக்கு அருகில் இழுக்க */
        margin-bottom: -10px !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #1E1E1E !important;
    }
    
    /* 4. MASTER OF WORLD CUISINE (ஆரஞ்சு நிறம் & டிசைன்) */
    h3 {
        text-align: center;
        margin-top: 0px !important;
        padding-top: 5px !important;
        color: #E67E22 !important; /* நல்ல ஆரஞ்சு நிறம் */
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase;
    }
    
    /* 5. Refresh Button Design */
    div.stButton > button {
        width: 100%;
        border-radius: 20px;
    }
    
    /* 6. தேவையில்லாதவற்றை மறைக்க */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 2. Display Logo (Perfectly Centered)
# 3 காலம்களைப் பயன்படுத்தி, நடுவில் லோகோவை வைக்கிறோம்
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if os.path.exists("myphoto.png"):
        st.image("myphoto.png", width=130)
    elif os.path.exists("myphoto.jpg"):
        st.image("myphoto.jpg", width=130)

# 3. Titles (Close gap & Colored)
st.markdown("<h1>VSP Chef</h1>", unsafe_allow_html=True)
st.markdown("<h3>MASTER OF WORLD CUISINE 🌎</h3>", unsafe_allow_html=True)

# 4. Refresh / Restart Button (சமையல் முடிந்ததும் மேலே வரும்)
if 'generated' not in st.session_state:
    st.session_state.generated = False

if st.session_state.generated:
    # சமையல் வந்த பிறகு, மேலே ஒரு 'New Recipe' பட்டன் வரும்
    if st.button("🔄 Start New Recipe (Click here to Clear)"):
        st.session_state.generated = False
        st.rerun()

# 5. API & Model Logic
model = None
api_key = None
if "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if api_key:
    try:
        clean_key = api_key.strip().replace('\n', '').replace('\r', '').replace('"', '').replace("'", "")
        genai.configure(api_key=clean_key)
        try:
            # Auto-detect model
            all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            chosen_model = next((m for m in all_models if 'flash' in m), None)
            if not chosen_model:
                chosen_model = next((m for m in all_models if 'pro' in m), 'gemini-pro')
            model = genai.GenerativeModel(chosen_model)
        except:
            model = genai.GenerativeModel('gemini-pro')
    except:
        st.error("Connection Issue")

# 6. Inputs
# சமையல் வரும்வரை மட்டுமே Input தெரியும், வந்த பிறகு Refresh பட்டன் மேலே இருக்கும்
if not st.session_state.generated:
    st.markdown("---") # ஒரு கோடு
    tab1, tab2 = st.tabs(["📝 Type Ingredients", "📷 Upload Photo"])
    user_query = ""
    user_img = None

    with tab1:
        txt = st.text_area("What ingredients do you have? (Any language)")
        if st.button("Get Recipe", type="primary"):
            user_query = txt

    with tab2:
        file = st.file_uploader("Upload fridge photo", type=['jpg', 'png', 'jpeg'])
        image_text = st.text_input("Add instructions (Optional):", placeholder="Ex: Make it spicy...")
        if file and st.button("Analyze & Cook", type="primary"):
            user_img = Image.open(file)
            user_query = image_text if image_text else "Identify ingredients and suggest a world-class recipe."

# 7. Cooking Logic
if 'user_query' in locals() and user_query and model:
    with st.spinner("VSP Chef is cooking..."):
        try:
            prompt = f"""
            You are VSP Chef, a world-renowned Master of World Cuisine.
            USER INPUT: "{user_query}"
            
            RULES:
            1. Reply in the USER'S LANGUAGE.
            2. Suggest a creative, delicious recipe.
            3. Provide step-by-step instructions.
            """
            
            if user_img:
                try: response = model.generate_content([prompt, user_img])
                except: response = model.generate_content(prompt)
            else:
                response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            st.balloons()
            st.success("Bon Appétit! - VSP Chef")
            
            # சமையல் முடிந்ததை உறுதிப்படுத்துகிறோம் (Refresh பட்டன் வர)
            st.session_state.generated = True
            
        except Exception as e:
            st.error(f"Error: {e}")
