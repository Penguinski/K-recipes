import streamlit as st
import google.generativeai as genai
import re
from typing import List, Dict

# =============================================================================
# 1. SETUP PAGINA - MOBILE FIRST
# =============================================================================
st.set_page_config(
    page_title="K Recipes",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "K Recipes - Gut Health Intelligence v2.0"}
)

# =============================================================================
# 2. DESIGN SYSTEM - MODERNE PALETTE CON CONTRASTI FORTI
# =============================================================================
st.markdown("""
<style>
    /* ====== VARIABILI COLORE ====== */
    :root {
        --primary: #FF6B35;        /* Arancio Saturo - CTA */
        --secondary: #004E89;      /* Blu Profondo - Accenti */
        --accent: #00D084;         /* Verde Smeraldo - Success */
        --warn: #FF1744;           /* Rosso Vivido - Alert */
        --dark: #0F1419;           /* Nero Profondo */
        --light: #F8F9FF;          /* Bianco Caldo */
        --gray: #6B7280;           /* Gray Neutro */
        --gradient-1: linear-gradient(135deg, #FF6B35 0%, #FF8C5A 100%);
        --gradient-2: linear-gradient(135deg, #004E89 0%, #0077B6 100%);
        --gradient-3: linear-gradient(135deg, #00D084 0%, #00FF9D 100%);
    }

    /* ====== RESET GLOBALE ====== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
        background: linear-gradient(180deg, #F8F9FF 0%, #EFF2FF 100%);
        color: #0F1419;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    }

    .stApp {
        background: linear-gradient(180deg, #F8F9FF 0%, #EFF2FF 100%) !important;
    }

    /* ====== HIDE DEFAULT STREAMLIT UI ====== */
    #MainMenu, header, footer {
        visibility: hidden !important;
        display: none !important;
    }

    .stMainBlockContainer {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 600px !important;
        margin: 0 auto !important;
    }

    /* ====== HEADER HERO ====== */
    .header-hero {
        text-align: center;
        padding: 2rem 0 1.5rem 0;
        background: var(--gradient-1);
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(255, 107, 53, 0.2);
        position: relative;
        overflow: hidden;
    }

    .header-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 200px;
        height: 200px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
    }

    .header-hero::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -5%;
        width: 150px;
        height: 150px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50%;
    }

    .logo-k {
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 0.9;
        letter-spacing: -4px;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        position: relative;
        z-index: 1;
    }

    .header-subtitle {
        font-size: 0.95rem;
        font-weight: 500;
        opacity: 0.95;
        letter-spacing: 1px;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }

    /* ====== FORM CONTAINER ====== */
    .form-container {
        background: white;
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(15, 20, 25, 0.08);
        border: 1px solid rgba(255, 107, 53, 0.1);
    }

    /* ====== LABELS CUSTOM ====== */
    label {
        font-weight: 700 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        color: #004E89 !important;
        display: block !important;
        margin-bottom: 0.75rem !important;
    }

    /* ====== SEGMENTED CONTROL (RADIO) ====== */
    div[role="radiogroup"] {
        background-color: #F0F4FF;
        padding: 6px;
        border-radius: 14px;
        display: flex !important;
        gap: 6px;
        margin-bottom: 2rem !important;
        border: 2px solid #004E89;
    }

    div[role="radiogroup"] > label {
        flex: 1;
        background: transparent !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        text-align: center !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #6B7280 !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 0 !important;
        border: none !important;
    }

    /* Active state */
    div[role="radiogroup"] > label[data-baseweb="radio"] {
        background: var(--gradient-1) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3) !important;
    }

    /* Hide radio circle */
    div[role="radiogroup"] label > span:first-child {
        display: none !important;
    }

    /* ====== TEXT INPUTS ====== */
    .stTextInput, .stTextArea {
        margin-bottom: 1.5rem !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: white !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        font-size: 16px !important;
        color: #0F1419 !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #9CA3AF !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border: 2px solid #FF6B35 !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
        outline: none !important;
    }

    /* ====== BUTTONS ====== */
    .stButton > button {
        background: var(--gradient-1) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        padding: 16px 24px !important;
        border-radius: 14px !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 8px 24px rgba(255, 107, 53, 0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(255, 107, 53, 0.4) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3) !important;
    }

    /* ====== RECIPE CARD ====== */
    .recipe-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 40px rgba(15, 20, 25, 0.08);
        border-left: 4px solid #FF6B35;
        animation: slideInUp 0.5s ease-out;
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .recipe-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #F0F4FF;
    }

    .recipe-emoji {
        font-size: 2.5rem;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.15);
    }

    .recipe-meta {
        flex: 1;
    }

    .recipe-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0F1419;
        line-height: 1.2;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem;
    }

    .recipe-time {
        font-size: 0.75rem;
        font-weight: 700;
        color: #FF6B35;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .recipe-tags {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }

    .tag {
        display: inline-block;
        padding: 4px 10px;
        background: #F0F4FF;
        color: #004E89;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    /* ====== INFO BOXES ====== */
    .info-box {
        padding: 12px 14px;
        border-radius: 12px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.5;
        font-weight: 500;
        border-left: 3px solid;
    }

    .glucose-box {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 0%);
        background: rgba(0, 208, 132, 0.12);
        color: #00A857;
        border-color: #00D084;
    }

    .chef-box {
        background: rgba(255, 107, 53, 0.12);
        color: #D84315;
        border-color: #FF6B35;
    }

    /* ====== SECTION CONTENT ====== */
    .section-label {
        font-weight: 800;
        font-size: 0.8rem;
        color: #004E89;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .content-text {
        font-size: 1rem;
        line-height: 1.6;
        color: #374151;
    }

    .ingredients-list {
        font-family: 'Menlo', 'Monaco', monospace;
        font-size: 0.95rem;
        line-height: 1.8;
        background: #F8F9FF;
        padding: 1rem;
        border-radius: 12px;
        border-left: 3px solid #00D084;
    }

    .procedure-text {
        font-size: 1rem;
        line-height: 1.7;
        color: #374151;
    }

    /* ====== SPINNER LOADING ====== */
    .stSpinner {
        color: #FF6B35 !important;
    }

    /* ====== ALERTS & MESSAGES ====== */
    .stAlert {
        border-radius: 14px !important;
    }

    [data-testid="stAlert"] {
        padding: 1rem !important;
        border-left: 4px solid !important;
    }

    /* Success */
    [data-testid="stAlert"] > div:first-child {
        background: rgba(0, 208, 132, 0.1) !important;
        border-left-color: #00D084 !important;
    }

    /* Error */
    [data-testid="stAlert"] svg {
        color: #FF1744 !important;
    }

    /* Info */
    [data-testid="stAlert"] {
        border-left-color: #0077B6 !important;
    }

    /* ====== SPACING ====== */
    .spacer {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* ====== RESPONSIVE MOBILE ====== */
    @media (max-width: 640px) {
        .logo-k {
            font-size: 3.5rem;
        }

        .form-container {
            padding: 1.5rem;
        }

        .recipe-card {
            padding: 1.2rem;
        }

        .recipe-title {
            font-size: 1.2rem;
        }
    }

</style>
""", unsafe_allow_html=True)

# =============================================================================
# 3. STATE MANAGEMENT
# =============================================================================
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = ""
    st.session_state.recipes = []

# =============================================================================
# 4. UTILITY FUNCTIONS
# =============================================================================
def parse_recipe(text: str) -> Dict[str, str]:
    """Parse recipe text into structured data"""
    recipe = {
        "EMOJI": "🍽️",
        "TITOLO": "Ricetta",
        "TEMPO": "20 min",
        "HACK": "Mantieni stabile il glucosio",
        "CHEF": "Aromatizza bene",
        "DESCRIZIONE": "",
        "INGREDIENTI": "",
        "PROCEDIMENTO": ""
    }
    
    # Split by keys
    lines = text.split('\n')
    current_key = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a key
        matched = False
        for key in recipe.keys():
            if line.startswith(f"{key}:"):
                current_key = key
                recipe[key] = line.replace(f"{key}:", "").strip()
                matched = True
                break
        
        # If no key match, append to current section
        if not matched and current_key:
            recipe[current_key] += " " + line
    
    return recipe

def sanitize_recipe(recipe: Dict[str, str]) -> Dict[str, str]:
    """Clean recipe data"""
    for key in recipe:
        recipe[key] = recipe[key].strip()
    return recipe

# =============================================================================
# 5. MAIN UI
# =============================================================================

# Header Hero
st.markdown("""
<div class="header-hero">
    <div class="logo-k">K.</div>
    <div class="header-subtitle">🥑 Gut Health Intelligence</div>
</div>
""", unsafe_allow_html=True)

# API Key Setup
if not st.session_state.google_api_key:
    with st.expander("🔑 CONNESSIONE API GEMINI", expanded=True):
        st.caption("Inserisci la tua Google Gemini API Key per abilitare lo Chef AI.")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write("")
        with col2:
            api_input = st.text_input(
                "API Key",
                type="password",
                placeholder="Incolla qui la tua chiave...",
                label_visibility="collapsed"
            )
            if api_input:
                st.session_state.google_api_key = api_input
                st.success("✅ API Key collegata! Puoi iniziare.")
                st.rerun()

# Main Form (visible only with API key)
if st.session_state.google_api_key:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # 1. Meal Type - Segmented Control
    st.markdown("**MOMENTO DELLA GIORNATA**")
    meal_type = st.radio(
        "Seleziona",
        ["☀️ Colazione", "🌤️ Pranzo", "☕ Merenda", "🌙 Cena"],
        horizontal=True,
        label_visibility="collapsed"
    )
    meal_type = meal_type.split()[-1]  # Extract just the word
    
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    
    # 2. Previous Meal Context
    st.markdown("**COSA HAI MANGIATO PRIMA?**")
    prev_meal = st.text_area(
        "Contesto",
        placeholder="Es. Pasta al sugo, Digiuno di 6 ore, Toast bianco...",
        height=90,
        label_visibility="collapsed"
    )
    
    # 3. Cravings
    st.markdown("**DI COSA HAI VOGLIA?**")
    craving = st.text_input(
        "Desideri",
        placeholder="Es. Salmone, qualcosa di caldo, poco elaborato...",
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    
    # Generate Button
    generate_btn = st.button("✨ Genera Menu Chef", key="generate")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # =============================================================================
    # 6. AI LOGIC & RENDERING
    # =============================================================================
    if generate_btn:
        if not prev_meal or not craving:
            st.warning("⚠️ Per favore compila tutti i campi per generare il menu.")
        else:
            with st.spinner("🤖 Lo Chef sta creando il tuo menu personalizzato..."):
                try:
                    genai.configure(api_key=st.session_state.google_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Sophisticated prompt
                    prompt = f"""
                    Tu sei un Personal Chef di livello mondiale specializzato in Gut Health e Nutrizione.
                    Stile: Bon Appétit + NYT Cooking + Scienza Nutrizionale.
                    
                    PROFILO CLIENTE:
                    - Intollerante al glutine
                    - Problematiche intestinali (Leaky Gut Syndrome)
                    - Ricerca stabilità glicemica
                    - Preferisce alimenti naturali e minimamente processati
                    
                    CONTESTO ATTUALE:
                    - Momento: {meal_type}
                    - Ultimo pasto: {prev_meal}
                    - Desiderio/Craving: {craving}
                    
                    LINEE GUIDA FERREE:
                    1. ZERO GLUTINE SEMPRE
                    2. Se pasto precedente era ricco di carboidrati → ora LOW CARB
                    3. Se a digiuno da >4 ore → proteina + grasso
                    4. COLAZIONE: SEMPRE salata/proteica (zero zuccheri semplici)
                    5. Evita: Latticini infiammatori, Oli vegetali, Zuccheri raffinati
                    6. Predilige: Grassi buoni (Ghee, Olio Evo, Avocado), Fermentati, Osso Brodo
                    
                    OUTPUT FORMAT: Genera ESATTAMENTE 3 opzioni diverse, separate da "|||"
                    
                    Per OGNI opzione, includi ESATTAMENTE queste righe (non di più, non di meno):
                    EMOJI: [Una emoji che rappresenta il piatto]
                    TITOLO: [Nome del piatto, creativo e appetibile]
                    TEMPO: [Tempo totale, es "15 min"]
                    HACK: [Consiglio SPECIFICO su glucosio/glicemia]
                    CHEF: [Consiglio di sapore/tecnica culinaria]
                    DESCRIZIONE: [Paragrafo 1-2 righe di introduzione]
                    INGREDIENTI: [Lista numerata con quantità]
                    PROCEDIMENTO: [Passaggi numerati, chiari e pratici]
                    
                    Sii creativo, pratico, appetibile. Ogni ricetta deve essere FACILMENTE PREPARABILE.
                    """
                    
                    response = model.generate_content(prompt)
                    response_text = response.text
                    
                    # Parse recipes
                    options = response_text.split("|||") if "|||" in response_text else [response_text]
                    
                    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
                    
                    # Render each recipe
                    for idx, opt in enumerate(options):
                        if opt.strip():
                            recipe = parse_recipe(opt.strip())
                            recipe = sanitize_recipe(recipe)
                            
                            # Render Card
                            st.markdown(f"""
                            <div class="recipe-card">
                                <div class="recipe-header">
                                    <div class="recipe-emoji">{recipe['EMOJI']}</div>
                                    <div class="recipe-meta">
                                        <div class="recipe-title">{recipe['TITOLO']}</div>
                                        <div class="recipe-time">⏱️ {recipe['TEMPO']}</div>
                                    </div>
                                </div>
                                
                                <div class="recipe-tags">
                                    <span class="tag">Gluten Free</span>
                                    <span class="tag">Gut Friendly</span>
                                    <span class="tag">Low Inflammatory</span>
                                </div>
                                
                                <div class="glucose-box">
                                    📉 <b>GLUCOSIO:</b> {recipe['HACK']}
                                </div>
                                
                                <div class="chef-box">
                                    👨‍🍳 <b>CHEF TIP:</b> {recipe['CHEF']}
                                </div>
                                
                                <p class="content-text" style="margin-top: 1rem; margin-bottom: 0.5rem; font-style: italic; color: #6B7280;">
                                    {recipe['DESCRIZIONE']}
                                </p>
                                
                                <div class="section-label">📋 Ingredienti</div>
                                <div class="ingredients-list">
                                    {recipe['INGREDIENTI'].replace(chr(10), '<br>')}
                                </div>
                                
                                <div class="section-label">👨‍🍳 Procedimento</div>
                                <p class="procedure-text">
                                    {recipe['PROCEDIMENTO'].replace(chr(10), '<br>')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.success("✅ Menu generato con successo!")
                
                except Exception as e:
                    st.error(f"❌ Errore nell'elaborazione: {str(e)}")
                    st.caption("Verifica la validità della tua API Key o riprova tra pochi istanti.")

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <p style="font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem;">
            🔓 Collega la tua API Key di Gemini per iniziare
        </p>
        <p style="font-size: 0.95rem; color: #9CA3AF;">
            Non hai una key? Ottieni gratuitamente su <b>ai.google.dev</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr style="margin-top: 3rem; border: 1px solid #E5E7EB; opacity: 0.3;">
<p style="text-align: center; font-size: 0.85rem; color: #9CA3AF; margin-top: 1.5rem;">
    K Recipes v2.0 • Made with ❤️ for Gut Health<br>
    Powered by Google Gemini • Hosted on Streamlit
</p>
""", unsafe_allow_html=True)
