import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64
import streamlit.components.v1 as components

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PATRIM Gestion", page_icon="🏢", layout="wide")

# --- PALETTE DE COULEURS ---
COLOR_ROUGE = "#8a0e01"
COLOR_VERT = "#2e7d32"
COLOR_GRIS = "#393939"
COLOR_ROSE = "#d35f52"
COLOR_BLEU_PATRIMOINE = "#34495e"
COLOR_BG_CARD = "#ffffff" 

# --- FONCTIONS UTILITAIRES ---
def get_file_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- FORMATAGE ---
def fmt(nombre):
    return f"{nombre:,.0f}".replace(",", ".")

# --- CSS INTELLIGENT (MOBILE VS ORDI) ---
bg_css = ""
arcades_path = get_file_path("arcades.png") 

if os.path.exists(arcades_path):
    try:
        img_bg_ext = get_img_as_base64(arcades_path)
        bg_css = f"""
        .arcades-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: url("data:image/png;base64,{img_bg_ext}");
            background-size: cover; background-position: center;
            opacity: 0.05; z-index: -1; pointer-events: none; mix-blend-mode: overlay;
        }}
        """
    except Exception: pass

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {{ --primary-red: {COLOR_ROUGE}; --text-grey: {COLOR_GRIS}; }}
    
    /* FOND ANIMÉ 3D */
    .background-container {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #f4f7f9; z-index: -3; overflow: hidden;
    }}
    .orb {{
        position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.6;
        animation: float 20s infinite ease-in-out alternate;
    }}
    .orb-1 {{ width: 70vh; height: 70vh; background: radial-gradient(circle, {COLOR_ROSE}, {COLOR_ROUGE}); top: -15%; left: -15%; animation-duration: 25s; }}
    .orb-2 {{ width: 60vh; height: 60vh; background: radial-gradient(circle, #ffdfba, {COLOR_ROSE}); bottom: -15%; right: -15%; animation-delay: -5s; animation-duration: 28s; }}
    .orb-3 {{ width: 40vh; height: 40vh; background: radial-gradient(circle, #ffffff, #dceefc); top: 40%; left: 40%; opacity: 0.8; animation: float-mid 35s infinite ease-in-out; }}
    
    @keyframes float {{ 0% {{ transform: translate(0, 0) rotate(0deg); }} 100% {{ transform: translate(-30px, 20px) rotate(-5deg); }} }}
    @keyframes float-mid {{ 0% {{ transform: translate(0, 0) scale(1); }} 50% {{ transform: translate(40px, -30px) scale(1.1); }} 100% {{ transform: translate(0, 0) scale(1); }} }}

    {bg_css}

    /* BASE */
    .stApp {{ background-color: transparent !important; font-family: 'Inter', sans-serif; color: var(--text-grey); }}
    [data-testid="stAppViewContainer"] {{ background-color: transparent !important; }}
    
    /* ELEMENTS COMMUNS */
    div[data-testid="stSidebarHeader"] {{ display: none; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 5rem !important; }}
    .logo-container-html {{ display: flex; justify-content: center; align-items: center; margin-bottom: 20px; margin-top: 20px; padding: 0; background: transparent !important; }}
    .custom-logo {{ width: 100% !important; max-width: 300px !important; height: auto; }}
    
    /* WIDGETS */
    .stSlider > div > div > div > div {{ background-color: {COLOR_ROUGE} !important; }} 
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{ background-color: #ffffff !important; color: {COLOR_GRIS} !important; border: 1px solid #e0e0e0; border-radius: 8px; }}
    button[data-testid="stNumberInputStepDown"], button[data-testid="stNumberInputStepUp"] {{ background-color: #ffffff !important; color: {COLOR_GRIS} !important; border-color: #e0e0e0 !important; font-weight: bold !important; }}

    /* KPI CARDS */
    .kpi-card {{ 
        background-color: rgba(255, 255, 255, 0.75); backdrop-filter: blur(15px);
        padding: 25px 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; position: relative; z-index: 1; transition: all 0.3s ease; height: 100%;
    }}
    .kpi-label {{ font-size: 0.8rem; font-weight: 600; color: #666; margin-bottom: 10px; }}
    .kpi-value {{ font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; }}
    .kpi-sub {{ font-size: 0.85rem; color: #888; margin-top: 8px; font-weight: 500; }}

    /* GRAPHIQUE */
    .graph-header {{ color: {COLOR_GRIS}; padding: 10px 0px; font-weight: 800; font-size: 1.2rem; text-align: left; margin-top: 5px; position: relative; z-index: 2; }}
    .graph-container {{ 
        background-color: rgba(255, 255, 255, 0.8); backdrop-filter: blur(15px);
        padding: 20px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 8px 30px rgba(0,0,0,0.03); position: relative; z-index: 1; margin-bottom: 20px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; background-color: transparent; border-bottom: none; }}
    .stTabs [data-baseweb="tab"] {{ height: 40px; border-radius: 20px; background-color: rgba(255,255,255,0.6); border: 1px solid rgba(0,0,0,0.05); color: {COLOR_GRIS}; font-weight: 600; padding: 0 20px; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ background-color: {COLOR_ROUGE}; color: white; border: none; }}

    /* CONTEXTE & CONCLUSION */
    .context-box, .conclusion-box {{
        background-color: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px);
        border-radius: 20px; padding: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid rgba(255,255,255,0.6);
    }}
    .context-title {{ font-weight: 700; text-transform: uppercase; font-size: 0.85rem; margin-bottom: 15px; letter-spacing: 1px; }}
    .context-text {{ color: {COLOR_GRIS}; font-size: 1.1rem; font-weight: 700; line-height: 1.4; letter-spacing: -0.5px; }}
    .conclusion-title {{ color: {COLOR_GRIS}; margin-top:0; margin-bottom: 25px; font-size: 1.6rem; font-weight: 800; letter-spacing: -1px; }}
    .conclusion-p {{ font-size: 1.15rem; line-height: 1.8; color: #555; margin-bottom: 20px; font-weight: 500; }}
    .highlight {{ font-weight: 700; color: {COLOR_GRIS}; background-color: rgba(255,255,255,0.5); padding: 2px 6px; border-radius: 4px; border:1px solid #eee; }}
    .highlight-red {{ font-weight: 800; color: {COLOR_ROUGE}; }}


    /* --- GESTION DES ECRANS --- */

    /* MODE ORDINATEUR (ECRANS > 768px) */
    @media (min-width: 769px) {{
        [data-testid="stSidebar"] {{ 
            min-width: 350px !important; 
            max-width: 350px !important;
            background-color: rgba(255, 255, 255, 0.65); 
            backdrop-filter: blur(25px);
            border-right: 1px solid rgba(255,255,255,0.4);
            box-shadow: 5px 0 20px rgba(0,0,0,0.03); 
        }}
    }}

    /* MODE MOBILE (ECRANS < 768px) */
    @media (max-width: 768px) {{
        /* Le menu prend tout l'écran quand il est ouvert pour être propre */
        [data-testid="stSidebar"] {{ 
            width: 100% !important; 
            min-width: 100% !important;
            background-color: #ffffff !important; /* Fond blanc opaque sur mobile */
            border-right: none;
        }}
        
        /* Ajustement des marges */
        .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; }}
        
        /* Titres plus petits */
        h1 {{ font-size: 1.8rem !important; }}
        .graph-header {{ font-size: 1rem !important; }}
        
        /* Cartes KPI compactes */
        .kpi-value {{ font-size: 1.6rem !important; }}
        .kpi-card {{ padding: 15px !important; margin-bottom: 10px !important; }}
        
        /* Cacher les décors lourds */
        .arcades-overlay {{ display: none !important; }}
        .orb {{ opacity: 0.3 !important; }}
    }}

    /* IMPRESSION */
    @media print {{
        @page {{ size: A4; margin: 10mm; }}
        .background-container, .arcades-overlay, [data-testid="stSidebar"], header, footer, .no-print {{ display: none !important; }}
        html, body, .stApp {{ background: white !important; }}
        .kpi-card, .graph-container, .context-box, .conclusion-box {{ box-shadow: none !important; border: 1px solid #ccc !important; page-break-inside: avoid; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- INJECTION 3D ---
st.markdown("""
<div class="background-container">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>
<div class="arcades-overlay"></div>
""", unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
if 'loyer_hc' not in st.session_state: st.session_state.loyer_hc = 600
if 'prov_mensuelle_input' not in st.session_state: st.session_state.prov_mensuelle_input = 50

def sync_widgets(key_slider, key_input): st.session_state[key_input] = st.session_state[key_slider]
def sync_widgets_reverse(key_input, key_slider): st.session_state[key_slider] = st.session_state[key_input]

with st.sidebar:
    logo_path = get_file_path("logo.png")
    if os.path.exists(logo_path):
        img_b64 = get_img_as_base64(logo_path)
        st.markdown(f'<div class="logo-container-html"><img src="data:image/png;base64,{img_b64}" class="custom-logo"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='margin-top:20px; text-align:center;'><h1 style='color:{COLOR_ROUGE}; font-size:3rem;'>PATRIM</h1></div>", unsafe_allow_html=True)

    # --- REVENUS ---
    st.markdown("### 🏠 Revenus & Charges")
    st.markdown("**Loyer Hors Charges (€)**")
    c1, c2 = st.columns([3, 2])
    with c1: st.slider("", 0, 5000, key='s_loyer', value=st.session_state.loyer_hc, step=10, on_change=sync_widgets, args=('s_loyer', 'loyer_hc'), label_visibility="collapsed")
    with c2: st.number_input("", 0, 5000, key='loyer_hc', value=st.session_state.loyer_hc, step=10, on_change=sync_widgets_reverse, args=('loyer_hc', 's_loyer'), label_visibility="collapsed", format="%d")

    # MODIFICATION 1 : PROVISION MENSUELLE
    st.caption("Charges Locatives")
    prov_mensuelle = st.number_input("Provision sur charges (Mensuel €)", value=st.session_state.prov_mensuelle_input, step=5, format="%d", help="Montant mensuel des provisions")

    # --- GESTION ---
    st.markdown("---")
    st.markdown("### 💼 Offre de Gestion")
    
    # MODIFICATION 2 : TAUX JUSQU'A 10%
    taux_gestion = st.slider("Honoraires Gestion TTC (%)", 4.0, 10.0, 5.0, 0.5)
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1: pno_active = st.checkbox("Option PNO (80€/an)", value=True)
    with col_opt2: gli_active = st.checkbox("Option GLI", value=True)
    
    # MODIFICATION 3 : CURSEUR GLI
    taux_gli = 2.8 # Valeur par défaut
    if gli_active:
        taux_gli = st.slider("Taux GLI (%)", 2.5, 2.8, 2.8, 0.1)

    # --- FINANCEMENT ---
    st.markdown("---")
    has_credit = st.checkbox("Crédit en cours sur ce bien ?", value=True)
    credit_mensuel_ass = 0
    montant_emprunte_initial = 0
    taux_credit_hors_ass = 0
    duree_restante_annees = 20

    if has_credit:
        st.caption("Flux de Trésorerie")
        credit_mensuel_ass = st.number_input("Mensualité Crédit (avec assurance) €", value=400, step=10, format="%d")
        st.caption("Calcul Patrimoine (Amortissement)")
        c_fin1, c_fin2 = st.columns(2)
        with c_fin1: montant_emprunte_initial = st.number_input("Capital Emprunté (€)", value=100000, step=1000, format="%d")
        with c_fin2: taux_credit_hors_ass = st.number_input("Taux Crédit (hors ass.) %", value=3.5, step=0.1, format="%.1f")
        duree_restante_annees = st.slider("Durée restante (années)", 5, 25, 20, 1)

    # --- ANALYSE POUSSÉE ---
    st.markdown("---")
    with st.expander("📊 Analyse Poussée (Rentabilité Nette)"):
        tf_annuelle = st.number_input("Taxe Foncière (Annuelle €)", value=800, step=50, format="%d")
        copro_annuelle = st.number_input("Charges Copro Propriétaire (Annuelle €)", value=400, step=50, format="%d", help="Charges non récupérables")
        st.markdown("**Stratégie Cashflow**")
        taux_placement = st.slider("Rendement placement (%)", 0.0, 15.0, 4.0, 0.5, help="Si cashflow positif")

# --- CALCULS MOTEUR ---
# 1. Revenus
loyer_cc = st.session_state.loyer_hc + prov_mensuelle

# 2. Dépenses Gestion
cout_gestion = loyer_cc * (taux_gestion / 100)
cout_gli = loyer_cc * (taux_gli / 100) if gli_active else 0
cout_pno = 80 / 12 if pno_active else 0
total_frais_gestion = cout_gestion + cout_gli + cout_pno
cashflow_brut_mensuel = loyer_cc - total_frais_gestion - credit_mensuel_ass
charges_proprio_mensuel = (tf_annuelle + copro_annuelle) / 12
cashflow_net_mensuel = cashflow_brut_mensuel - charges_proprio_mensuel

# --- DONNÉES GRAPHIQUES ---
nb_mois_projection = duree_restante_annees * 12
annees_axis = list(range(1, duree_restante_annees + 1))

# Cashflow Cumulé
data_cashflow_cumul = []
cumul_cf = 0
for m in range(1, nb_mois_projection + 1):
    if cashflow_net_mensuel > 0: cumul_cf = (cumul_cf + cashflow_net_mensuel) * (1 + taux_placement/100/12)
    else: cumul_cf += cashflow_net_mensuel
    if m % 12 == 0: data_cashflow_cumul.append(cumul_cf)

# Patrimoine Cumulé
data_patrimoine_cumul = []
capital_rembourse_total = 0
remaining_balance = montant_emprunte_initial
taux_mensuel_credit = taux_credit_hors_ass / 100 / 12
mensualite_theorique_ha = 0
if has_credit and montant_emprunte_initial > 0 and taux_credit_hors_ass > 0:
    mensualite_theorique_ha = montant_emprunte_initial * (taux_mensuel_credit / (1 - (1 + taux_mensuel_credit) ** (-nb_mois_projection)))

for m in range(1, nb_mois_projection + 1):
    interet_mois = remaining_balance * taux_mensuel_credit
    capital_mois = mensualite_theorique_ha - interet_mois
    if remaining_balance > 0:
        capital_rembourse_total += capital_mois
        remaining_balance -= capital_mois
    if m % 12 == 0:
        patrimoine_at_year = data_cashflow_cumul[m//12 -1] + capital_rembourse_total
        data_patrimoine_cumul.append(patrimoine_at_year)

# --- PAGE PRINCIPALE ---
st.markdown(f"<h1 style='color:{COLOR_GRIS}; margin-bottom:0; font-weight: 800; letter-spacing: -1px;'>Étude de Gestion Locative</h1>", unsafe_allow_html=True)
st.caption(f"Analyse pour un loyer de {fmt(st.session_state.loyer_hc)} € HC")
st.write("")

# KPI CARDS
k1, k2, k3, k4 = st.columns(4)
def kpi(label, val, sub, color_code):
    return f"""<div class="kpi-card" style="border-left: 4px solid {color_code};">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color: {color_code};">{val}</div>
                <div class="kpi-sub">{sub}</div>
               </div>"""

color_cf = COLOR_VERT if cashflow_net_mensuel >= 0 else COLOR_ROUGE
txt_cf = "Cashflow Positif" if cashflow_net_mensuel >= 0 else "Effort d'épargne"

with k1: st.markdown(kpi("Loyer Charges Comprises", f"{fmt(loyer_cc)} €", f"Dont {fmt(prov_mensuelle)}€ provisions", COLOR_ROUGE), unsafe_allow_html=True)
with k2: st.markdown(kpi("Total Frais Gestion", f"{fmt(total_frais_gestion)} €", f"Taux eff: {total_frais_gestion/loyer_cc*100:.1f}% TTC", COLOR_GRIS), unsafe_allow_html=True)
with k3: st.markdown(kpi("Reste à Vivre (Brut)", f"{fmt(cashflow_brut_mensuel)} €", "Avant TF et Charges Proprio", color_cf), unsafe_allow_html=True)
with k4: st.markdown(kpi("Cashflow Net Réel", f"{fmt(cashflow_net_mensuel)} €", txt_cf, color_cf), unsafe_allow_html=True)

# --- ZONE GRAPHIQUE ---
st.write("")
col_graph, col_context = st.columns([3, 1])

with col_graph:
    st.markdown('<div class="graph-header">Projection Financière</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["💰 Flux de Trésorerie (Cashflow)", "🏛️ Enrichissement Latent (Patrimoine)"])
    
    config = {'displayModeBar': False, 'scrollZoom': False}
    axis_style = dict(showgrid=False, showline=False, zeroline=False, tickfont=dict(color='#999', size=11, family='Inter'), fixedrange=True)
    yaxis_style = dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', gridwidth=1, showline=False, zeroline=False, tickfont=dict(color='#999', size=11), tickprefix="€ ", fixedrange=True)
    layout_common = dict(
        separators=",.", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        margin=dict(t=30, b=30, l=10, r=10), height=350,
        hovermode="x unified", hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter", bordercolor="rgba(0,0,0,0.1)"),
        xaxis=dict(**axis_style, title="Années"), yaxis=dict(**yaxis_style)
    )

    with tab1:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        fig1 = go.Figure()
        color_line1 = COLOR_VERT if cashflow_net_mensuel >= 0 else COLOR_ROUGE
        fig1.add_trace(go.Scatter(x=annees_axis, y=data_cashflow_cumul, mode='lines+markers', name='Cumul', line=dict(width=3, color=color_line1, shape='spline'), marker=dict(size=6, color='white', line=dict(width=2, color=color_line1))))
        fig1.update_layout(**layout_common, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True, config=config)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=annees_axis, y=data_patrimoine_cumul, mode='lines+markers', name='Patrimoine', line=dict(width=3, color=COLOR_BLEU_PATRIMOINE, shape='spline'), marker=dict(size=6, color='white', line=dict(width=2, color=COLOR_BLEU_PATRIMOINE)), fill='tozeroy', fillcolor="rgba(52, 73, 94, 0.1)"))
        fig2.update_layout(**layout_common, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config=config)
        st.markdown('</div>', unsafe_allow_html=True)

# --- CONTEXTE ---
with col_context:
    st.write("") 
    st.write("") 
    if cashflow_net_mensuel > 0:
        titre_ctx, color_ctx = "Rentabilité Positive", COLOR_VERT
        msg_ctx = f"Surplus de <b>{fmt(cashflow_net_mensuel*12)} €/an</b>."
    elif cashflow_net_mensuel > -100:
        titre_ctx, color_ctx = "Opération Équilibrée", "#f39c12"
        msg_ctx = f"Effort minime ({fmt(abs(cashflow_net_mensuel))}€/mois)."
    else:
        titre_ctx, color_ctx = "Effort d'Épargne", COLOR_ROUGE
        msg_ctx = f"Apport mensuel de <b>{fmt(abs(cashflow_net_mensuel))} €</b>."

    st.markdown(f"""
    <div class="context-box" style="border-left: 4px solid {color_ctx}; height: 340px; display:flex; flex-direction:column; justify-content:center;">
        <div class="context-title" style="color: {color_ctx};">{titre_ctx}</div>
        <div class="context-text">{msg_ctx}</div>
        <div class="context-sub">Analyse PATRIM Gestion.</div>
    </div>
    """, unsafe_allow_html=True)

# --- CONCLUSION ---
frais_details = [f"Honoraires: {taux_gestion}%"]
if gli_active: frais_details.append(f"GLI: {taux_gli}%")
if pno_active: frais_details.append("PNO: 80€/an")
frais_str = " + ".join(frais_details)
valeur_finale = data_patrimoine_cumul[-1] if data_patrimoine_cumul else 0
gain_str = "gain patrimonial" if valeur_finale > 0 else "coût total"
col_gain = COLOR_BLEU_PATRIMOINE if valeur_finale > 0 else COLOR_ROUGE

conclusion_html = f"""
<div class="conclusion-box no-print-shadow">
    <h3 class="conclusion-title">Synthèse de votre Gestion</h3>
    <p class="conclusion-p">
        Pour un bien loué <span class="highlight">{fmt(loyer_cc)} € CC</span>, l'Agence PATRIM assure une gestion pour 
        <span class="highlight-red">{fmt(total_frais_gestion)} €/mois</span> ({frais_str}).
    </p>
    <p class="conclusion-p">
        Résultat net mensuel : <span style="color:{COLOR_VERT if cashflow_net_mensuel>=0 else COLOR_ROUGE}; font-weight:800;">{fmt(cashflow_net_mensuel)} €</span>.
    </p>
    <p class="conclusion-p" style="margin-bottom:0; border-top: 1px solid #eee; padding-top: 20px;">
        <b>Projection sur {duree_restante_annees} ans :</b><br>
        Enrichissement latent estimé à <span style="color:{col_gain}; font-size: 1.3rem; font-weight:800;">{fmt(valeur_finale)} €</span>.
    </p>
</div>
"""
st.markdown(conclusion_html, unsafe_allow_html=True)

# --- PIED DE PAGE & PRINT ---
st.markdown(f"<div style='text-align:center; color:#999; margin-top:20px; margin-bottom: 40px; font-size:0.8rem;'>Agence PATRIM Toulouse - Simulation Confidentielle</div>", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🖨️ Imprimer")
    components.html("""
        <button onclick="window.print()" style="background-color: #8a0e01; border: none; color: white; padding: 10px 20px; border-radius: 8px; font-family: sans-serif; width: 100%; font-weight: 600; cursor: pointer;">🖨️ Imprimer PDF</button>
        """, height=60)