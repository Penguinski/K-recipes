import streamlit as st
import google.generativeai as genai
import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURAZIONE PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="K Recipes",
    page_icon="🥑",
    layout="centered", # Meglio "centered" su mobile per colonna singola
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. CSS "DARK PREMIUM" (Ottimizzato per iPhone OLED)
# -----------------------------------------------------------------------------
# Questo CSS crea un look nativo, nasconde elementi inutili e crea carte in stile "Glass" scuro.
css = """
<style>
    /* RESET E FONT NATIVO IOS */
    html, body, [class*="css"]  {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #ffffff;
    }

    /* SFONDO ONYX/MIDNIGHT */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
        background-attachment: fixed;
    }

    /* TITOLI */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    /* NASCONDI MENU STREAMLIT E FOOTER */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;} /* Nasconde la barra colorata in alto */

    /* AGGIUSTAMENTO MARGINI IPHONE (Evita il Notch) */
    .block-container {
        padding-top: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 100% !important;
    }

    /* INPUT FIELDS (Stile Scuro) */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }
    .stSelectbox > div > div > div {
        color: white !important;
    }
    
    /* LABEL DEGLI INPUT */
    label {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 0.9rem !important;
    }

    /* BOTTONE PRINCIPALE (Gradiente Neon) */
    div.stButton > button {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        padding: 16px 24px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border-radius: 16px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
        transition: transform 0.2s;
    }
    div.stButton > button:active {
        transform: scale(0.98);
    }

    /* CARTE RICETTA (Glassmorphism Scuro) */
    .recipe-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .recipe-title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 10px;
        background: -webkit-linear-gradient(0deg, #c4b5fd, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .tag-box {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 12px;
    }
    .tag-time { background: rgba(56, 189, 248, 0.2); color: #7dd3fc; }
    .tag-gut { background: rgba(52, 211, 153, 0.2); color: #6ee7b7; border: 1px solid rgba(52, 211, 153, 0.3); }
    .tag-hack { background: rgba(251, 146, 60, 0.2); color: #fdba74; border: 1px solid rgba(251, 146, 60, 0.3); }

    /* Separatore */
    hr { border-color: rgba(255,255,255,0.1); }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. GESTIONE API KEY (Senza Sidebar)
# -----------------------------------------------------------------------------
# Se non c'è la chiave, mostriamo un box ben visibile in alto
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = ""

# Se la chiave è vuota, mostra l'expander APERTO di default
is_key_missing = st.session_state.google_api_key == ""

with st.expander("🔑 Impostazioni & API Key", expanded=is_key_missing):
    api_input = st.text_input(
        "Inserisci la tua Google Gemini API Key:", 
        type="password", 
        value=st.session_state.google_api_key,
        help="La chiave serve per generare le ricette. Viene salvata solo per questa sessione."
    )
    if api_input:
        st.session_state.google_api_key = api_input
        # Se l'utente ha appena inserito la chiave, ricarichiamo la pagina per chiudere il box visivamente (opzionale ma pulito)
        if is_key_missing:
            st.rerun()

# -----------------------------------------------------------------------------
# 4. INTERFACCIA UTENTE
# -----------------------------------------------------------------------------

# Saluto
hour = datetime.datetime.now().hour
if 5 <= hour < 12: greeting = "Buongiorno"
elif 12 <= hour < 18: greeting = "Buon pomeriggio"
else: greeting = "Buonasera"

st.markdown(f"# 🥑 K Recipes")
st.markdown(f"_{greeting}! Il tuo chef personale per l'intestino è pronto._")
st.write("") # Spaziatura

# Form di Input
with st.container():
    meal_type = st.selectbox("🍽️ Che pasto vuoi fare?", ["Colazione", "Pranzo", "Merenda", "Cena"], index=1)
    
    c1, c2 = st.columns(2)
    with c1:
        prev_meal = st.text_area("🔙 Cos'hai mangiato prima?", placeholder="Es. Pasta (carbo), Digiuno...", height=100)
    with c2:
        craving = st.text_input("😋 Di cosa hai voglia?", placeholder="Es. Salmone, Zucchine, Qualcosa di caldo...")
    
    st.write("")
    generate_btn = st.button("Genera Menu Chef ✨")

# -----------------------------------------------------------------------------
# 5. LOGICA AI
# -----------------------------------------------------------------------------
def get_ai_response(api_key, meal, prev, want):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Agisci come uno Chef esperto (stile Serious Eats) e Nutrizionista per Leaky Gut.
    
    UTENTE: Intollerante glutine, permeabilità intestinale.
    CONTESTO: Pasto: {meal}. Mangiato prima: {prev}. Voglia: {want}.
    
    REGOLE:
    1. Se prima ha mangiato Carboidrati -> ORA SOLO LOW CARB/KETO (Proteine+Grassi).
    2. ZERO GLUTINE.
    3. COLAZIONE: Solo salata o grassi sani.
    
    OUTPUT:
    Genera 3 opzioni brevi separate da "|||".
    
    Per ogni opzione usa questo formato HTML/Markdown esatto:
    # [EMOJI] Nome Piatto
    TEMPO: 15 min (esempio)
    BENEFICIO: (Spiegazione scientifica breve)
    HACK: (Consiglio glucosio: es. mangia prima le verdure)
    CHEF: (Consiglio tecnico sapore)
    RICETTA: Ingredienti e passaggi rapidi.
    """
    
    response = model.generate_content(prompt)
    return response.text

# -----------------------------------------------------------------------------
# 6. GENERAZIONE E OUTPUT
# -----------------------------------------------------------------------------
if generate_btn:
    if not st.session_state.google_api_key:
        st.error("⚠️ Per favore inserisci la API Key nel pannello 'Impostazioni' in alto.")
    else:
        with st.spinner("🍳 Elaborazione menu in corso..."):
            try:
                result = get_ai_response(st.session_state.google_api_key, meal_type, prev_meal, craving)
                st.session_state.last_result = result
            except Exception as e:
                st.error(f"Errore: {e}")

# Mostra risultati se presenti
if "last_result" in st.session_state:
    st.write("")
    raw_text = st.session_state.last_result
    
    # Parsing delle 3 opzioni
    if "|||" in raw_text:
        options = raw_text.split("|||")
    else:
        options = [raw_text]
    
    # Visualizzazione Cards
    for opt in options:
        if opt.strip():
            # Pulizia e formattazione visuale
            # Rimuoviamo il markdown header standard per usarne uno custom
            lines = opt.strip().split('\n')
            title = lines[0].replace('#', '').strip()
            body = '\n'.join(lines[1:])
            
            # Rendering della Card
            st.markdown(f"""
            <div class="recipe-card">
                <div class="recipe-title">{title}</div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #e2e8f0;">
                    {body.replace('BENEFICIO:', '<br><b>🧬 Beneficio:</b>').replace('HACK:', '<br><b>📉 Glucose Hack:</b>').replace('CHEF:', '<br><b>👨‍🍳 Chef Tip:</b>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
