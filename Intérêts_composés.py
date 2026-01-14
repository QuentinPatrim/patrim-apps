import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="COMPOUND // VISION",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME COLORS ---
NEON_GREEN = "#00FFA3"
NEON_PURPLE = "#BC13FE"
NEON_BLUE = "#2962FF"
DARK_BG = "#050505"
DARK_CARD = "#111111"
TEXT_COLOR = "#E0E0E0"

# --- CSS DARK FINTECH ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');

    /* BASE */
    .stApp {{
        background-color: {DARK_BG};
        color: {TEXT_COLOR};
        font-family: 'Inter', sans-serif;
    }}
    
    /* TITRES */
    h1, h2, h3 {{
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: -1px;
        color: white !important;
    }}
    h1 span {{ color: {NEON_GREEN}; }}

    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }}
    
    /* INPUTS */
    .stNumberInput input, .stSlider > div {{
        background-color: #1a1a1a !important;
        color: {NEON_GREEN} !important;
        border: 1px solid #333;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
    }}
    .stNumberInput label, .stSlider label {{
        color: #888 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
    }}

    /* METRIC CARDS */
    .metric-container {{
        background: linear-gradient(145deg, {DARK_CARD}, #0a0a0a);
        border: 1px solid #222;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: transform 0.2s;
    }}
    .metric-container:hover {{
        border-color: {NEON_GREEN};
        transform: translateY(-2px);
        box-shadow: 0 0 15px rgba(0, 255, 163, 0.1);
    }}
    .metric-label {{
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 5px;
    }}
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.1);
    }}
    .metric-sub {{
        font-size: 0.9rem;
        color: {NEON_GREEN};
    }}

    /* CUSTOM DIVIDER */
    hr {{ border-color: #222; margin: 30px 0; }}

    /* PLOTLY FIX */
    .js-plotly-plot .plotly .modebar {{ display: none !important; }}
    
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("## // PARAMÈTRES")
    st.markdown("---")
    
    initial_investment = st.number_input("CAPITAL INITIAL (€)", value=10000, step=1000)
    monthly_dca = st.number_input("DCA MENSUEL (€)", value=500, step=50)
    
    st.markdown("---")
    st.markdown("### PERFORMANCE ACTION")
    stock_growth = st.slider("Croissance Prix / An (%)", 0.0, 20.0, 6.0, 0.5, help="Hausse du cours de l'action hors dividendes")
    dividend_yield = st.slider("Rendement Dividende / An (%)", 0.0, 15.0, 4.0, 0.5, help="Dividende versé (et réinvesti)")
    dividend_growth = st.slider("Croissance du Dividende / An (%)", 0.0, 20.0, 2.0, 0.5, help="Augmentation annuelle du versement")
    
    st.markdown("---")
    years = st.slider("HORIZON (ANNÉES)", 5, 50, 20, 1)
    
    tax_rate = st.slider("Impôt sur PV/Dividendes (%)", 0, 50, 30, 1) / 100

# --- MOTEUR DE CALCUL (The Snowball Engine) ---
months = years * 12
data = []

current_portfolio = initial_investment
total_invested = initial_investment
current_dividend_yield = dividend_yield / 100

# Pour suivre le flux de dividendes annuel
annual_dividends_log = []
year_dividends = 0

for m in range(1, months + 1):
    # 1. Ajout du DCA
    current_portfolio += monthly_dca
    total_invested += monthly_dca
    
    # 2. Calcul du dividende mensuel (simplifié pour lissage)
    # On applique le rendement actuel au portefeuille
    monthly_div = current_portfolio * (current_dividend_yield / 12)
    
    # 3. Réinvestissement du dividende (Brut pour l'effet boule de neige, imposition à la sortie ou annuelle selon stratégie, ici on simule un compte type PEA/CTO capitalisant)
    # Note: Dans une simulation pure compound, on réinvestit tout. 
    # Pour le réalisme, on peut retirer les taxes ici ou à la fin. 
    # Option choisie : Réinvestissement NET (si Flat Tax appliquée au fil de l'eau) ou BRUT.
    # Pour montrer la puissance, on assume souvent une enveloppe fiscale (PEA) ou réinvestissement brut.
    # Appliquons une taxe légère fictive ou 0 pour montrer la puissance brute, ajustons à la fin.
    current_portfolio += monthly_div 
    year_dividends += monthly_div
    
    # 4. Appréciation du prix de l'action
    current_portfolio *= (1 + (stock_growth / 100) / 12)
    
    # Fin d'année : Augmentation du dividende (Dividend Growth)
    if m % 12 == 0:
        current_dividend_yield *= (1 + (dividend_growth / 100))
        annual_dividends_log.append(year_dividends)
        year_dividends = 0
        
        data.append({
            "Mois": m,
            "Année": m // 12,
            "Investi": total_invested,
            "Valeur": current_portfolio,
            "Rente Annuelle Brute": current_portfolio * current_dividend_yield
        })

df = pd.DataFrame(data)

# --- KPI CALCULATIONS ---
final_value = df.iloc[-1]["Valeur"]
final_invested = df.iloc[-1]["Investi"]
total_gains = final_value - final_invested
net_value = final_value - (total_gains * tax_rate) # Taxe à la sortie sur la plus-value totale
final_annual_income = df.iloc[-1]["Rente Annuelle Brute"]
monthly_passive_income = final_annual_income / 12

multiplier = final_value / final_invested

# --- MAIN INTERFACE ---

# Header
st.markdown(f"<h1>COMPOUND <span>//</span> VISION</h1>", unsafe_allow_html=True)
st.markdown("<div style='margin-top: -15px; color: #666; font-family: JetBrains Mono; margin-bottom: 30px;'>SYSTÈME DE PROJECTION PATRIMONIALE AVANCÉ</div>", unsafe_allow_html=True)

# Top KPIs
c1, c2, c3, c4 = st.columns(4)

def kpi_card(col, label, value, sub_value, color=NEON_GREEN):
    with col:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color: {color}">{value}</div>
            <div class="metric-sub">{sub_value}</div>
        </div>
        """, unsafe_allow_html=True)

kpi_card(c1, "VALEUR PORTEFEUILLE", f"{final_value:,.0f} €".replace(",", " "), f"Investi: {final_invested:,.0f} €")
kpi_card(c2, "RENTE PASSIVE / MOIS", f"{monthly_passive_income:,.0f} €".replace(",", " "), "Dividendes bruts", NEON_PURPLE)
kpi_card(c3, "PLUS-VALUE TOTALE", f"+{total_gains:,.0f} €".replace(",", " "), f"Net après impôt: {net_value:,.0f} €", NEON_BLUE)
kpi_card(c4, "MULTIPLICATEUR", f"x {multiplier:.2f}", "Effet Levier Temps", "#FFFFFF")

st.markdown("---")

# --- CHART AREA ---
col_chart, col_details = st.columns([3, 1])

with col_chart:
    st.markdown("### ⚡ TRAJECTOIRE EXPONENTIELLE")
    
    fig = go.Figure()

    # Zone Investissement (Base)
    fig.add_trace(go.Scatter(
        x=df["Année"], 
        y=df["Investi"],
        fill='tozeroy',
        mode='none',
        name='Capital Investi',
        fillcolor='rgba(255, 255, 255, 0.1)'
    ))

    # Ligne Valeur (Compound)
    fig.add_trace(go.Scatter(
        x=df["Année"], 
        y=df["Valeur"],
        mode='lines',
        name='Valeur Composée',
        line=dict(color=NEON_GREEN, width=3),
        fill='tonexty',
        fillcolor='rgba(0, 255, 163, 0.05)' # Glow vert léger
    ))

    # Layout Dark Fintech
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(
            showgrid=True, gridcolor='#222', 
            tickfont=dict(color='#666', family='JetBrains Mono'),
            title=dict(text="ANNÉES", font=dict(color='#444'))
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#222', 
            tickfont=dict(color='#666', family='JetBrains Mono'),
            tickprefix="€ "
        ),
        showlegend=False,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_details:
    st.markdown("### 📑 ANALYSE")
    
    # Progress Bar Style Custom
    def custom_progress(label, value, max_val, color):
        pct = min(100, (value / max_val) * 100)
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <div style="display:flex; justify-content:space-between; color:#888; font-size:0.8rem; font-family:JetBrains Mono; margin-bottom:5px;">
                <span>{label}</span>
                <span>{int(pct)}%</span>
            </div>
            <div style="width:100%; background:#222; height:6px; border-radius:3px;">
                <div style="width:{pct}%; background:{color}; height:6px; border-radius:3px; box-shadow: 0 0 10px {color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Ratio Investi vs Intérêts
    share_invested = (final_invested / final_value) * 100
    share_compound = 100 - share_invested
    
    st.markdown(f"""
    <div style="background:{DARK_CARD}; padding:15px; border-radius:8px; border:1px solid #222; margin-bottom:20px;">
        <div style="color:#aaa; font-size:0.9rem; margin-bottom:10px;">COMPOSITION FINALE</div>
        <div style="font-size:1.5rem; color:white; font-weight:bold; font-family:JetBrains Mono;">
            <span style="color:#666">{share_invested:.0f}%</span> / <span style="color:{NEON_GREEN}">{share_compound:.0f}%</span>
        </div>
        <div style="color:#666; font-size:0.7rem;">EFFORT / INTÉRÊTS</div>
    </div>
    """, unsafe_allow_html=True)

    # Dividend Income Evolution
    st.markdown("### 💸 FLUX DIVIDENDES")
    
    # Mini chart pour les dividendes
    fig_div = go.Figure()
    fig_div.add_trace(go.Bar(
        x=df["Année"],
        y=df["Rente Annuelle Brute"],
        marker_color=NEON_PURPLE,
        opacity=0.8
    ))
    fig_div.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        bargap=0.1
    )
    st.plotly_chart(fig_div, use_container_width=True)
    
    st.markdown(f"""
    <div style="text-align:right; font-family:JetBrains Mono; font-size:0.8rem; color:{NEON_PURPLE}">
        Dernière année : {final_annual_income:,.0f} € / an
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #444; font-size: 0.8rem; font-family: 'JetBrains Mono';">
    SIMULATION À TITRE INDICATIF • <span style="color:{NEON_GREEN}">POWERED BY COMPOUND VISION</span>
</div>
""", unsafe_allow_html=True)
