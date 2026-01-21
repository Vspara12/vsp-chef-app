hide_styles = """
<style>
/* Main menu & header hide */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}

/* Footer முழுக்க மறைக்க */
footer {visibility: hidden;}
footer {pointer-events: none !important;}

/* Streamlit badge (bottom-right) hide */
div[class*="viewerBadge"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

div[data-testid="stViewerBadge"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* Extra safety: any fixed bottom-right element */
div[style*="position: fixed"][style*="bottom"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_styles, unsafe_allow_html=True)
