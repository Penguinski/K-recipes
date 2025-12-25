import streamlit as st
import google.generativeai as genai
import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURAZIONE PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="K Recipes",
    page_icon="🥑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. CSS "EDITORIAL MINIMAL" (High Contrast, Bold Typography)
# -----------------------------------------------------------------------------
css = """
<style>
    /* IMPORT FONT MODERN (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* RESET GLOBALE */
    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, sans-serif;
        background-color: #000000;
        color: #ffffff;
    }

    /* SFONDO NERO ASSOLUTO (OLED) */
    .stApp {
        background-color: #000000;
        background-image: none;
    }

    /* TITOLI BOLD & BIG */
    h1 {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -2px !important;
        line-height: 1 !important;
        color: #ffffff !important;
        margin-bottom: 0.5rem !important;
    }
    h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        color: #f2f2f7 !important;
    }

    /* NASCONDI UI STREAMLIT */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        padding-bottom: 4rem !important;
    }

    /* INPUT FIELDS (Stile iOS Dark) */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        background-color: #1c1c1e !important; /* Grigio Apple Dark */
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        font-size: 16px !important; /* Evita zoom su iOS */
        padding: 12px !important;
    }
    
    /* LABEL DEGLI INPUT (Upper, small, tracking) */
    label {
        color: #8e8e93 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        margin-bottom: 8px !important;
    }

    /* BOTTONE PRINCIPALE (Solid White on Black - High Contrast) */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        padding: 18px 24px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        width: 100% !important;
        transition: transform 0.1s;
    }
    div.stButton > button:active {
        transform: scale(0.97);
        background-color: #e5e5e5 !important;
    }

    /* CARTE RICETTA (Minimal, Solid) */
    .recipe-card {
        background-color: #1c1c1e;
        border: 1px solid #333;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }
    
    .recipe-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .recipe-emoji {
        font-size: 2rem;
        margin-right: 12px;
    }
    
    .recipe-title {
        font-size: 1.4rem;
        font-weight: 800;
        line-height: 1.2;
        color: #ffffff;
    }

    /* TAGS & BADGES */
    .meta-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 6px 10px;
        border-radius: 6px;
        margin-right: 6px;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
    }
    .tag-time { background-color: #333; color: #aaa; }
    .tag-hack { background-color: #2c2c2e; color: #a29bfe; border: 1px solid #5f55fa; } /* Viola Neon */

    /* TESTI INTERNI */
    .section-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #8e8e93;
        margin-top: 16px;
        margin-bottom: 4px;
        text-transform: uppercase;
    }
    .body-text {
        font-size: 1rem;
        line-height: 1.5;
        color: #e5e5ea;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. GESTIONE API KEY
# -----------------------------------------------------------------------------
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = ""

is_key_missing = st.session_state.google_api_key == ""

with st.expander("⚙️ IMPOSTAZIONI", expanded=is_key_missing):
    api_input = st.text_input(
        "API KEY", 
        type="password", 
        value=st.session_state.google_api_key,
        placeholder="Incolla qui la tua chiave Gemini"
    )
    if api_input:
        st.session_state.google_api_key = api_input
        if is_key_missing:
            st.rerun()

# -----------------------------------------------------------------------------
# 4. INTERFACCIA UTENTE
# -----------------------------------------------------------------------------

# Header Minimal
st.markdown("<h1>K Recipes.</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8e8e93; font-size: 1.1rem; margin-top: -10px; margin-bottom: 30px;'>Nutrizione Funzionale & Alta Cucina.</p>", unsafe_allow_html=True)

# Input Form
with st.container():
    meal_type = st.selectbox("MOMENTO", ["Colazione", "Pranzo", "Merenda", "Cena"], index=1)
    
    st.write("") # Spacer
    
    prev_meal = st.text_area("CONTESTO METABOLICO", placeholder="Cosa hai mangiato prima? Es. Digiuno, Pasta...", height=80)
    craving = st.text_input("VOGLIE / FRIGO", placeholder="Es. Salmone, qualcosa di veloce...")
    
    st.write("")
    st.write("")
    generate_btn = st.button("GENERA MENU")

# -----------------------------------------------------------------------------
# 5. LOGICA AI
# -----------------------------------------------------------------------------
def get_ai_response(api_key, meal, prev, want):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Sei un Personal Chef (stile Serious Eats) e Nutrizionista Funzionale.
    
    CLIENTE: Intollerante glutine, Leaky Gut, vuole evitare picchi glicemici.
    SITUAZIONE: Pasto: {meal}. Mangiato prima: {prev}. Voglie: {want}.
    
    REGOLE:
    1. Se prima carboidrati -> ORA SOLO LOW CARB.
    2. ZERO GLUTINE.
    3. COLAZIONE: Solo salata o proteica.
    
    OUTPUT:
    Genera 3 opzioni separate da "|||". 
    Usa esattamente questo formato per ogni opzione (senza markdown headers #, usa solo testo):

    EMOJI: [Inserisci Emoji]
    TITOLO: [Nome Piatto]
    TEMPO: [Es. 15 min]
    HACK: [Consiglio glucosio breve]
    DESCRIZIONE: [Spiegazione del perché fa bene e come farlo saporito, max 3 frasi]
    INGREDIENTI: [Lista breve]
    """
    
    response = model.generate_content(prompt)
    return response.text

# -----------------------------------------------------------------------------
# 6. OUTPUT
# -----------------------------------------------------------------------------
if generate_btn:
    if not st.session_state.google_api_key:
        st.error("INSERISCI API KEY")
    else:
        with st.spinner("ANALISI IN CORSO..."):
            try:
                result = get_ai_response(st.session_state.google_api_key, meal_type, prev_meal, craving)
                st.session_state.last_result = result
            except Exception as e:
                st.error(f"Errore: {e}")

if "last_result" in st.session_state:
    st.write("")
    raw_text = st.session_state.last_result
    options = raw_text.split("|||") if "|||" in raw_text else [raw_text]
    
    for opt in options:
        if opt.strip():
            # Parsing manuale semplice
            lines = [l for l in opt.strip().split('\n') if l.strip()]
            
            # Valori di default
            emoji = "🥑"
            title = "Ricetta Chef"
            time = "15 min"
            hack = "Mangia proteine prima"
            desc = ""
            
            # Estrazione dati (molto semplice per robustezza)
            content_html = ""
            for line in lines:
                if "EMOJI:" in line: emoji = line.replace("EMOJI:", "").strip()
                elif "TITOLO:" in line: title = line.replace("TITOLO:", "").strip()
                elif "TEMPO:" in line: time = line.replace("TEMPO:", "").strip()
                elif "HACK:" in line: hack = line.replace("HACK:", "").strip()
                else: content_html += f"<div>{line}</div>"

            # Rendering Card Minimal
            st.markdown(f"""
            <div class="recipe-card">
                <div class="recipe-header">
                    <div class="recipe-emoji">{emoji}</div>
                    <div class="recipe-title">{title}</div>
                </div>
                <div>
                    <span class="meta-tag tag-time">{time}</span>
                    <span class="meta-tag tag-hack">GLUCOSE HACK</span>
                </div>
                <div class="section-title">Why & How</div>
                <div class="body-text" style="margin-bottom: 10px; color: #ccc;">
                    <em>{hack}</em>
                </div>
                <div class="body-text">
                    {content_html.replace('DESCRIZIONE:', '').replace('INGREDIENTI:', '<br><b>INGREDIENTI:</b>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
