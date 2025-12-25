import streamlit as st
import google.generativeai as genai
import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURAZIONE PAGINA E STATO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="K Recipes | Gut Health Chef",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inizializzazione Session State
if "generated_recipes" not in st.session_state:
    st.session_state.generated_recipes = None
if "last_prompt_hash" not in st.session_state:
    st.session_state.last_prompt_hash = ""

# -----------------------------------------------------------------------------
# 2. CSS AVANZATO (Glassmorphism, 3D Emojis, Gradienti)
# -----------------------------------------------------------------------------
css = """
<style>
    /* IMPORT FONT (Opzionale, pulito) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* SFONDO GRADIENTE VIBRANTE (Copre tutto) */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* RIMOZIONE PADDING E UI STREAMLIT */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    header, footer {
        visibility: hidden !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }

    /* STILE 3D PER LE EMOJI (Titoli) */
    .emoji-3d {
        font-size: 4rem;
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.3));
        transition: transform 0.3s ease;
        display: inline-block;
    }
    .emoji-3d:hover {
        transform: scale(1.1) rotate(10deg);
    }
    
    .title-text {
        font-size: 3rem; 
        font-weight: 800;
        color: white;
        text-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        margin-bottom: 0px;
    }
    
    .subtitle-text {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 2rem;
    }

    /* CONTAINER INPUT (Glassmorphism leggero) */
    .input-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        margin-bottom: 2rem;
    }

    /* STILE WIDGET STREAMLIT (Adattamento al tema) */
    .stTextInput > label, .stSelectbox > label, .stTextArea > label {
        color: white !important;
        font-weight: 600;
        font-size: 1rem;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: none !important;
        border-radius: 12px !important;
        color: #333 !important;
    }

    /* BOTTONE ACTION (Centrale e Vibrante) */
    div.stButton > button {
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        color: white;
        border: none;
        padding: 0.8rem 2.5rem;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        border-radius: 50px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.5);
    }
    div.stButton > button:active {
        transform: translateY(1px);
    }

    /* CARD RICETTE (Glassmorphism spinto) */
    .recipe-card {
        background: rgba(255, 255, 255, 0.85); /* Più opaco per leggibilità testo */
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 25px;
        color: #1a1a1a;
        height: 100%;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .recipe-card:hover {
        transform: translateY(-5px);
    }
    .recipe-card h3 {
        color: #e52e71;
        font-weight: 800;
        border-bottom: 2px solid rgba(0,0,0,0.05);
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .recipe-card strong {
        color: #2c3e50;
    }
    
    /* Titoli dentro le card per Hack e Why */
    .highlight-box {
        background: rgba(231, 60, 126, 0.1);
        border-left: 4px solid #e73c7e;
        padding: 10px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR (API KEY)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Impostazioni")
    api_key = st.text_input("Gemini API Key", type="password", help="Inserisci la tua chiave API di Google Gemini")
    st.markdown("---")
    st.caption("K Recipes v1.0 • Gut Protocol")

# -----------------------------------------------------------------------------
# 4. HEADER & INPUT UI
# -----------------------------------------------------------------------------

# Calcolo saluto dinamico
current_hour = datetime.datetime.now().hour
if 5 <= current_hour < 12:
    greeting = "Buongiorno"
elif 12 <= current_hour < 18:
    greeting = "Buon pomeriggio"
else:
    greeting = "Buonasera"

col_head1, col_head2 = st.columns([1, 4])
with col_head1:
    st.markdown('<div class="emoji-3d">🥑</div>', unsafe_allow_html=True)
with col_head2:
    st.markdown(f'<h1 class="title-text">K Recipes</h1><p class="subtitle-text">{greeting}. Cuciniamo qualcosa che fa bene al tuo intestino.</p>', unsafe_allow_html=True)

# Input Container
st.markdown('<div class="input-container">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    meal_type = st.selectbox("Per quale pasto?", ["Colazione", "Pranzo", "Merenda", "Cena"], index=1)
    prev_meal = st.text_area("Cosa hai mangiato nel pasto precedente?", placeholder="Es. Pasta al pomodoro (molti carbo), oppure Digiuno...", height=100)
with c2:
    ingredients = st.text_input("Voglie o Ingredienti disponibili", placeholder="Es. Salmone, Zucchine, 'Qualcosa di croccante'")
    
    # Spazio vuoto per allineare il bottone visivamente
    st.write("") 
    st.write("") 
    generate_btn = st.button("✨ Genera Proposte K")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. LOGICA AI (GEMINI)
# -----------------------------------------------------------------------------
def build_prompt(meal, prev, craving):
    return f"""
    Sei un Personal Chef d'élite (mix tra Kenji López-Alt e Yotam Ottolenghi) specializzato in nutrizione clinica per Intolleranza al Glutine (NCGS) e Leaky Gut.
    
    IL TUO UTENTE:
    - Soffre di permeabilità intestinale (Leaky Gut).
    - Deve evitare picchi glicemici (Glucose Goddess style).
    - Ama il cibo gourmet, odia le ricette banali.
    
    CONTESTO ATTUALE:
    - Pasto: {meal}
    - Pasto Precedente (Analisi Metabolica): {prev} (SE ha mangiato carboidrati prima, ORA proponi rigorosamente LOW CARB/KETO. Se ha digiunato, bilancia bene).
    - Voglie/Ingredienti: {craving}
    
    REGOLE DIETETICHE IMPERATIVE:
    1. ZERO GLUTINE.
    2. COLAZIONE: Solo salata o grassi/proteine (es. Yogurt greco), mai dolce zuccherino.
    3. GLUCOSE HACK: Includi sempre un consiglio per ridurre la curva glicemica specifico per la ricetta.
    
    GENERA 3 OPZIONI DISTINTE (Output separato da "|||"):
    
    OPZIONE 1: 🚀 "Fast & Functional" (Veloce, max 15min, focus densità nutrizionale).
    OPZIONE 2: 🍲 "Deep Nourish" (Caldo, brodoso o cotto lentamente, easy digestion).
    OPZIONE 3: ✨ "The Vibe / Gourmet" (Contrasti, texture, acidità, impiattamento figo).
    
    FORMATO RISPOSTA PER OGNI OPZIONE (Usa Markdown):
    ### [Emoji 3D pertinente] Nome Piatto Creativo
    **⏱️ Tempo & Difficoltà**
    
    <div class="highlight-box">
    <b>🧬 Perché ti fa bene:</b> Spiegazione scientifica sintetica legata al Leaky Gut.
    </div>

    <div class="highlight-box">
    <b>📉 Glucose Hack:</b> Il trucco per la glicemia (es. ordine degli ingredienti, aceto prima, ecc).
    </div>
    
    **👨‍🍳 Il Tocco da Chef:** (Tecnica per elevare il sapore).
    
    **Ingredienti & Procedimento:** (Conciso, bullet points).
    """

if generate_btn:
    if not api_key:
        st.error("⚠️ Inserisci la tua Google Gemini API Key nella sidebar per iniziare.")
    else:
        try:
            with st.spinner("🍳 Lo Chef sta analizzando il tuo metabolismo..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = build_prompt(meal_type, prev_meal, ingredients)
                response = model.generate_content(prompt)
                
                # Salvataggio in sessione
                st.session_state.generated_recipes = response.text
                
        except Exception as e:
            st.error(f"Qualcosa è andato storto: {e}")

# -----------------------------------------------------------------------------
# 6. OUTPUT AREA (3 Cards)
# -----------------------------------------------------------------------------
if st.session_state.generated_recipes:
    st.markdown("---")
    
    # Gestione split della risposta (se l'AI ha rispettato il separatore) o display semplice
    content = st.session_state.generated_recipes
    
    # Provo a dividere se il separatore è presente, altrimenti mostro tutto
    if "|||" in content:
        options = content.split("|||")
        # Pulisco eventuali spazi vuoti
        options = [opt.strip() for opt in options if opt.strip()]
    else:
        # Fallback se l'AI non ha separato bene
        options = [content]

    # Layout a colonne responsive (su mobile Streamlit impila automaticamente)
    cols = st.columns(len(options))
    
    for idx, option_text in enumerate(options):
        with cols[idx]:
            # Injecting HTML wrapper for Glassmorphism card
            st.markdown(f"""
            <div class="recipe-card">
                {option_text}
            </div>
            """, unsafe_allow_html=True)

# Footer invisibile per spacing
st.markdown("<br><br>", unsafe_allow_html=True)
