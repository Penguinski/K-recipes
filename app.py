import streamlit as st
import google.generativeai as genai
import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURAZIONE PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="K Recipes",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. CSS "EDITORIAL LIGHT" (Clean, Fast, Minimal)
# -----------------------------------------------------------------------------
css = """
<style>
    /* RESET & SYSTEM FONTS (Caricamento istantaneo su mobile) */
    html, body, [class*="css"]  {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        background-color: #ffffff; /* Sfondo Bianco Puro */
        color: #111111; /* Nero Inchiostro per leggibilità */
    }

    /* SFONDO */
    .stApp {
        background-color: #ffffff;
    }

    /* TITOLI (Stile Rivista) */
    h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px !important;
        color: #000000 !important;
        margin-bottom: 0px !important;
        line-height: 1.1 !important;
    }
    p.subtitle {
        font-size: 1.1rem;
        color: #666666;
        font-weight: 500;
        margin-top: 5px;
        margin-bottom: 30px;
    }

    /* INPUT FIELDS (Stile "Surface") */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        background-color: #f3f4f6 !important; /* Grigio chiarissimo */
        color: #000000 !important;
        border: 1px solid #e5e7eb !important; /* Bordo sottile */
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 16px !important; /* No zoom su iOS */
        box-shadow: none !important;
    }
    
    /* Focus degli input */
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        background-color: #ffffff !important;
        border: 1px solid #000000 !important; /* Bordo nero al focus */
    }

    /* LABELS (Piccole, Uppercase) */
    label {
        color: #333333 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 6px !important;
    }

    /* BOTTONE PRINCIPALE (Nero Solido - High Contrast) */
    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 16px 24px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        width: 100% !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.1s;
    }
    div.stButton > button:active {
        transform: scale(0.98);
        background-color: #333333 !important;
    }

    /* CARTE RICETTA (Stile "Paper") */
    .recipe-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); /* Ombra sofficissima */
        transition: transform 0.2s;
    }
    
    .recipe-header {
        display: flex;
        align-items: flex-start;
        margin-bottom: 16px;
    }
    
    .recipe-emoji {
        font-size: 2.5rem;
        margin-right: 16px;
        line-height: 1;
        background: #f9fafb;
        padding: 10px;
        border-radius: 12px;
    }
    
    .recipe-title {
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1.2;
        color: #000000;
        letter-spacing: -0.5px;
    }

    /* TAGS */
    .tag-container {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .meta-tag {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 6px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }
    .tag-time { background-color: #f3f4f6; color: #4b5563; }
    .tag-hack { background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; } /* Verde Smeraldo */
    .tag-chef { background-color: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; } /* Arancio Bruciato */

    /* TESTO CORPO */
    .section-label {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 4px;
        margin-top: 16px;
    }
    .body-text {
        font-size: 1rem;
        line-height: 1.6;
        color: #374151; /* Grigio scuro per lettura */
    }
    
    /* HACK VISIBILE */
    .hack-box {
        background-color: #f0fdf4;
        border-left: 3px solid #16a34a;
        padding: 12px;
        border-radius: 0 8px 8px 0;
        color: #166534;
        font-size: 0.95rem;
        margin-top: 10px;
        font-weight: 500;
    }

    /* PULIZIA INTERFACCIA MOBILE */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        max-width: 100%;
    }
    #MainMenu, footer, header { visibility: hidden; }
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
        "API KEY GOOGLE", 
        type="password", 
        value=st.session_state.google_api_key,
        placeholder="Incolla qui la chiave..."
    )
    if api_input:
        st.session_state.google_api_key = api_input
        if is_key_missing:
            st.rerun()

# -----------------------------------------------------------------------------
# 4. INTERFACCIA PRINCIPALE
# -----------------------------------------------------------------------------

# Header
st.markdown("<h1>K Recipes.</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Cucina Intelligente per il tuo Intestino.</p>", unsafe_allow_html=True)

# Input Form
with st.container():
    meal_type = st.selectbox("CHE PASTO PREPARIAMO?", ["Colazione", "Pranzo", "Merenda", "Cena"], index=1)
    
    c1, c2 = st.columns(2)
    with c1:
        prev_meal = st.text_area("COSA HAI MANGIATO PRIMA?", placeholder="Es. Pasta (carbo), Niente...", height=100)
    with c2:
        craving = st.text_input("VOGLIE / INGREDIENTI", placeholder="Es. Salmone, veloce...")
        # Spaziatore visivo per allineare altezza su desktop
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        
    generate_btn = st.button("CREA IL MENU")

# -----------------------------------------------------------------------------
# 5. LOGICA AI
# -----------------------------------------------------------------------------
def get_ai_response(api_key, meal, prev, want):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt ottimizzato per risposte strutturate
    prompt = f"""
    Sei un Personal Chef (stile Serious Eats/Bon Appetit) e Nutrizionista Funzionale.
    
    CLIENTE: Intollerante glutine, Leaky Gut, vuole evitare picchi glicemici.
    CONTESTO: Pasto={meal}. Precedente={prev}. Voglie={want}.
    
    REGOLE:
    1. Se prima carboidrati -> ORA LOW CARB (Proteine/Grassi/Verdure).
    2. ZERO GLUTINE.
    3. COLAZIONE: Solo salata o grassi sani.
    
    OUTPUT:
    Genera 3 opzioni separate da "|||". 
    Formatta ogni opzione SOLO con queste chiavi esatte (una per riga):

    EMOJI: [Emoji singola]
    TITOLO: [Nome Piatto Creativo]
    TEMPO: [Es. 15 min]
    HACK: [Consiglio glucosio in una frase]
    CHEF: [Consiglio tecnico sul sapore in una frase]
    DESCRIZIONE: [Breve intro appetitosa]
    INGREDIENTI: [Lista separata da virgole]
    PROCEDIMENTO: [Passaggi brevi]
    """
    
    response = model.generate_content(prompt)
    return response.text

# -----------------------------------------------------------------------------
# 6. OUTPUT VISIVO
# -----------------------------------------------------------------------------
if generate_btn:
    if not st.session_state.google_api_key:
        st.error("Inserisci prima la API Key nelle impostazioni sopra.")
    else:
        with st.spinner("Lo Chef sta pensando..."):
            try:
                result = get_ai_response(st.session_state.google_api_key, meal_type, prev_meal, craving)
                st.session_state.last_result = result
            except Exception as e:
                st.error(f"Errore: {e}")

if "last_result" in st.session_state:
    st.write("") # Spacer
    raw_text = st.session_state.last_result
    # Split opzioni
    options = raw_text.split("|||") if "|||" in raw_text else [raw_text]
    
    for opt in options:
        if opt.strip():
            # Parsing "fatto in casa" molto robusto
            lines = [l for l in opt.strip().split('\n') if l.strip()]
            data = {
                "EMOJI": "🍽️", "TITOLO": "Ricetta Chef", "TEMPO": "20 min",
                "HACK": "Mangia fibre prima", "CHEF": "Usa sale di qualità",
                "DESCRIZIONE": "", "INGREDIENTI": "", "PROCEDIMENTO": ""
            }
            
            current_key = None
            for line in lines:
                # Controlla se la linea inizia con una delle chiavi note
                found_key = False
                for key in data.keys():
                    if line.startswith(f"{key}:"):
                        current_key = key
                        data[key] = line.replace(f"{key}:", "").strip()
                        found_key = True
                        break
                # Se non è una chiave, appendi al valore della chiave corrente
                if not found_key and current_key:
                    data[current_key] += " " + line

            # Rendering della Card Light
            st.markdown(f"""
            <div class="recipe-card">
                <div class="recipe-header">
                    <div class="recipe-emoji">{data['EMOJI']}</div>
                    <div class="recipe-info">
                        <div class="recipe-title">{data['TITOLO']}</div>
                        <div class="tag-container">
                            <span class="meta-tag tag-time">⏱ {data['TEMPO']}</span>
                        </div>
                    </div>
                </div>

                <div class="hack-box">
                    📉 <b>GLUCOSE HACK:</b> {data['HACK']}
                </div>

                <div class="section-label">Perché ti piacerà</div>
                <div class="body-text">{data['DESCRIZIONE']}</div>
                
                <div class="section-label">Tocco dello Chef</div>
                <div class="body-text" style="color: #c2410c;">👨‍🍳 {data['CHEF']}</div>

                <div class="section-label">Ingredienti</div>
                <div class="body-text" style="font-family: monospace; font-size: 0.9rem; color: #555;">
                    {data['INGREDIENTI']}
                </div>
                
                <div class="section-label">Procedimento</div>
                <div class="body-text">
                    {data['PROCEDIMENTO']}
                </div>
            </div>
            """, unsafe_allow_html=True)
