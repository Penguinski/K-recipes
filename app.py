import streamlit as st
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. SETUP PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="K Recipes",
    page_icon="🥑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. CSS "APP NATIVE STYLE" (Fix Mobile loading + High Design)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* -----------------------------------------------------------
       RESET & FONT DI SISTEMA (Velocità Massima su Mobile)
    ----------------------------------------------------------- */
    html, body, [class*="css"]  {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #FAFAFA; /* Grigio chiarissimo "App Background" */
        color: #000000;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        background-color: #FAFAFA;
    }

    /* -----------------------------------------------------------
       HEADER GRAFICO
    ----------------------------------------------------------- */
    .header-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        text-align: left;
    }
    .big-k {
        font-size: 5rem;
        font-weight: 900;
        line-height: 0.8;
        letter-spacing: -3px;
        color: #000000;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 1.1rem;
        font-weight: 500;
        color: #666666;
        letter-spacing: -0.5px;
    }

    /* -----------------------------------------------------------
       NASCONDI ELEMENTI DI DEFAULT BRUTTI
    ----------------------------------------------------------- */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 600px; /* Limita larghezza su Desktop per sembrare app */
    }

    /* -----------------------------------------------------------
       WIDGET STYLING (Trasformazione Totale)
    ----------------------------------------------------------- */
    
    /* RADIO BUTTONS (Diventano Pillole/Tabs) */
    div[role="radiogroup"] {
        background-color: #E5E5EA; /* Grigio Apple */
        padding: 4px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        margin-bottom: 25px;
    }
    div[role="radiogroup"] > label {
        flex: 1;
        background-color: transparent;
        border: none;
        margin: 0;
        padding: 8px 0;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        color: #8E8E93;
        transition: all 0.2s;
        cursor: pointer;
    }
    div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: #FFFFFF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000;
    }
    /* Nascondiamo il pallino del radio button */
    div[role="radiogroup"] label div:first-child {
        display: none; 
    }

    /* TEXT INPUTS (Stile "Card Conversazionale") */
    .stTextArea, .stTextInput {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 0px; /* Il padding lo gestisce l'input interno */
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 15px;
    }
    
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border: 2px solid transparent !important; /* Nessun bordo visibile di default */
        padding: 16px !important;
        font-size: 17px !important; /* Dimensione nativa iOS */
        border-radius: 16px !important;
    }
    
    /* Focus state */
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border: 2px solid #000000 !important;
    }

    /* LABELS */
    .stTextArea label, .stTextInput label {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #8E8E93 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding-left: 5px;
    }

    /* BOTTONE "ACTION" (Nero, Largo, Shadow) */
    div.stButton > button {
        background-color: #000000 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 18px !important;
        border-radius: 16px !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important;
        margin-top: 10px;
    }
    div.stButton > button:active {
        transform: scale(0.98);
        background-color: #333 !important;
    }

    /* -----------------------------------------------------------
       CARD RICETTE (Stile Editoriale)
    ----------------------------------------------------------- */
    .recipe-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.02);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    .emoji-circle {
        font-size: 2.5rem;
        background: #F2F2F7;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
    }
    .recipe-title {
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.5px;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .recipe-meta {
        font-size: 0.9rem;
        font-weight: 600;
        color: #8E8E93;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 20px;
    }
    
    /* HACK & CHEF BOXES */
    .info-box {
        padding: 12px 16px;
        border-radius: 12px;
        font-size: 0.95rem;
        line-height: 1.4;
        margin-bottom: 12px;
        font-weight: 500;
    }
    .hack-box { background: #E8F5E9; color: #1B5E20; }
    .chef-box { background: #FFF3E0; color: #E65100; }
    
    .section-head {
        font-weight: 800;
        font-size: 0.9rem;
        margin-top: 20px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .content-text {
        color: #3A3A3C;
        font-size: 1rem;
        line-height: 1.6;
    }

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. GESTIONE STATO & API
# -----------------------------------------------------------------------------
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = ""

# -----------------------------------------------------------------------------
# 4. INTERFACCIA (UI)
# -----------------------------------------------------------------------------

# Header
st.markdown("""
<div class="header-container">
    <div class="big-k">K.</div>
    <div class="subtitle">Gut Health & Kitchen Intelligence.</div>
</div>
""", unsafe_allow_html=True)

# Impostazioni (Minimal)
if not st.session_state.google_api_key:
    with st.expander("🔌 CONNESSIONE AI (Richiesto)", expanded=True):
        st.caption("Inserisci la tua Google Gemini API Key per attivare lo Chef.")
        st.session_state.google_api_key = st.text_input("API KEY", type="password", label_visibility="collapsed", placeholder="Incolla API Key qui...")

# Form (Card Style)
if st.session_state.google_api_key:
    
    # 1. Pasto (Segmented Control / Tabs)
    st.caption("MOMENTO DELLA GIORNATA")
    meal_type = st.radio(
        "Scegli Pasto", 
        ["Colazione", "Pranzo", "Merenda", "Cena"], 
        horizontal=True, 
        label_visibility="collapsed"
    )

    st.write("") # Spacer

    # 2. Contesto (Conversational Inputs)
    prev_meal = st.text_area(
        "CONTESTO", 
        placeholder="Cosa hai mangiato prima? (Es. Pasta, Digiuno...)", 
        height=80
    )
    
    craving = st.text_input(
        "DESIDERI", 
        placeholder="Di cosa hai voglia? (Es. Salmone, qualcosa di caldo...)"
    )

    st.write("") # Spacer

    # 3. Bottone
    generate_btn = st.button("Genera Menu Chef")


    # -----------------------------------------------------------------------------
    # 5. LOGICA AI & OUTPUT
    # -----------------------------------------------------------------------------
    if generate_btn:
        with st.spinner("Creazione menu in corso..."):
            try:
                genai.configure(api_key=st.session_state.google_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')

                prompt = f"""
                Sei un Personal Chef (stile Bon Appetit / NYT Cooking) specializzato in Leaky Gut.
                
                CLIENTE: Intollerante glutine, Leaky Gut, vuole stabilità glicemica.
                MOMENTO: {meal_type}. PRECEDENTE: {prev_meal}. VOGLIA: {craving}.
                
                LOGICA FERREA:
                1. Se prima carboidrati -> ORA SOLO LOW CARB.
                2. ZERO GLUTINE.
                3. COLAZIONE: Solo salata/proteica.
                
                OUTPUT: Genera 3 opzioni separate da "|||". 
                Usa questo formato esatto (chiave:valore):
                
                EMOJI: [Emoji]
                TITOLO: [Nome Piatto Cool]
                TEMPO: [Tempo]
                HACK: [Consiglio glucosio]
                CHEF: [Consiglio sapore]
                DESCRIZIONE: [Intro]
                INGREDIENTI: [Lista breve]
                PROCEDIMENTO: [Passaggi]
                """
                
                response = model.generate_content(prompt)
                
                # Parsing e Display
                options = response.text.split("|||") if "|||" in response.text else [response.text]
                
                st.write("") # Spacer prima dei risultati
                
                for opt in options:
                    if opt.strip():
                        # Parse lines
                        lines = [l for l in opt.strip().split('\n') if l.strip()]
                        d = {k: "" for k in ["EMOJI", "TITOLO", "TEMPO", "HACK", "CHEF", "DESCRIZIONE", "INGREDIENTI", "PROCEDIMENTO"]}
                        
                        curr = None
                        for line in lines:
                            for k in d.keys():
                                if line.startswith(f"{k}:"):
                                    curr = k
                                    d[k] = line.replace(f"{k}:", "").strip()
                                    break
                            else:
                                if curr: d[curr] += " " + line
                        
                        # Fallbacks
                        if not d["EMOJI"]: d["EMOJI"] = "🍽️"
                        
                        # Render Card
                        st.markdown(f"""
                        <div class="recipe-card">
                            <div class="card-header">
                                <div class="emoji-circle">{d['EMOJI']}</div>
                                <div style="text-align:right; font-weight:700; color:#8E8E93; font-size:0.8rem;">
                                    {d['TEMPO'].upper()}
                                </div>
                            </div>
                            
                            <div class="recipe-title">{d['TITOLO']}</div>
                            <div class="recipe-meta">Gluten Free • Gut Friendly</div>
                            
                            <div class="hack-box">📉 <b>GLUCOSE:</b> {d['HACK']}</div>
                            <div class="chef-box">👨‍🍳 <b>CHEF TIP:</b> {d['CHEF']}</div>
                            
                            <p class="content-text" style="margin-top:15px; font-style:italic; color:#666;">
                                {d['DESCRIZIONE']}
                            </p>
                            
                            <div class="section-head">INGREDIENTI</div>
                            <p class="content-text" style="font-family:'Menlo', monospace; font-size:0.85rem;">
                                {d['INGREDIENTI']}
                            </p>
                            
                            <div class="section-head">PROCEDIMENTO</div>
                            <p class="content-text">
                                {d['PROCEDIMENTO']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Errore: {e}")

else:
    # Stato vuoto (quando non c'è API key)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.info("👆 Inserisci la tua API Key sopra per iniziare.")
