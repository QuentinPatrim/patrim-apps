import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64
import urllib.parse

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Simulateur Prêt PATRIM", page_icon="🏦", layout="centered")

# --- COULEURS & STYLE ---
COLOR_ROUGE = "#8a0e01"
COLOR_GRIS = "#393939"
COLOR_ROSE_PATRIM = "#d35f52"
COLOR_VERT = "#2e7d32"
COLOR_BLEU = "#34495e"

# --- UTILITAIRES ---
def get_file_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

def get_img_as_base64(file_path):
    with open(file_path, "rb") as f: data = f.read()
    return base64.b64encode(data).decode()

def fmt(nombre): return f"{nombre:,.0f}".replace(",", ".")

# --- CSS AVANCÉ ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
    
    /* CONFIG DE BASE */
    .stApp {{ background-color: #f4f7f9; font-family: 'Inter', sans-serif; overflow-x: hidden; }}
    
    /* FORCE TEXTE GRIS FONCÉ */
    .stApp p, .stApp label, .stApp span, .stApp div, h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_GRIS} !important;
    }}
    .stCaption {{ color: #666666 !important; }}

    /* LOGO CENTRÉ ET IMPOSANT */
    [data-testid="stHeader"] {{ background-color: transparent; }}
    .logo-container {{ display: flex; justify-content: center; align-items: center; margin-bottom: 30px; margin-top: 10px; }}
    .custom-logo-img {{ width: 320px; height: auto; }} 

    /* STYLE DU CONTENEUR DE CONTACT */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: white;
        border: 1px solid #e0e0e0;
        border-left: 6px solid {COLOR_ROUGE} !important;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }}

    /* RESULTAT CARD PRINCIPALE */
    .main-result-card {{
        background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
        padding: 30px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center;
        border: 1px solid rgba(255,255,255,0.5); margin-bottom: 25px; border-top: 5px solid {COLOR_ROUGE};
    }}
    .result-val-big {{ font-size: 3.5rem; font-weight: 800; color: {COLOR_ROUGE} !important; line-height: 1.1; margin-bottom: 10px; }}
    .result-label-big {{ font-size: 1.1rem; font-weight: 700; color: #666 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }}
    .result-sub-val {{ font-size: 1.2rem; font-weight: 600; color: {COLOR_BLEU} !important; }}

    /* BOUTON D'ACTION */
    .contact-btn {{
        display: block; width: 100%; background: linear-gradient(45deg, {COLOR_ROUGE}, {COLOR_ROSE_PATRIM}); color: white !important; 
        text-align: center; padding: 18px; border-radius: 12px; font-weight: 800; font-size: 1.1rem;
        text-decoration: none; transition: 0.3s; margin-top: 25px; box-shadow: 0 6px 20px rgba(138, 14, 1, 0.3);
    }}
    .contact-btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(138, 14, 1, 0.4); }}
    
    /* INPUTS */
    .stNumberInput input {{ background-color: white !important; color: {COLOR_GRIS} !important; border-radius: 8px; font-weight: 600; }}
    .stSlider > div > div > div > div {{ background-color: {COLOR_ROUGE} !important; }}
    .stRadio > div {{ background-color: rgba(255,255,255,0.5); padding: 10px; border-radius: 12px; border: 1px solid #eee; display: flex; justify-content: center; gap: 20px; }}

    /* CACHER L'INTERFACE STREAMLIT */
    #MainMenu, footer, header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
logo_path = get_file_path("logo.png")
if os.path.exists(logo_path):
    img_b64 = get_img_as_base64(logo_path)
    st.markdown(f"""<div class="logo-container"><img src="data:image/png;base64,{img_b64}" class="custom-logo-img"></div>""", unsafe_allow_html=True)
else:
    st.markdown(f"<h1 style='text-align:center; color:{COLOR_ROUGE}; font-size: 3rem;'>PATRIM FINANCE</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Simulateur de Financement</h2>", unsafe_allow_html=True)

# --- SÉLECTEUR DE MODE ---
mode_calcul = st.radio("", [" Calculer une Mensualité", " Ma Capacité d'emprunt"], horizontal=True, label_visibility="collapsed")

# --- INPUTS ---
st.markdown("### 1. Paramètres du Projet")

if mode_calcul == " Calculer une Mensualité":
    c1, c2 = st.columns(2)
    with c1:
        # Renommé pour plus de clarté
        montant_projet_input = st.number_input("Montant du Projet (€)", value=250000, step=1000, format="%d", help="Prix du bien + Frais de notaire")
        duree_annees = st.slider("Durée (années)", 7, 30, 20, 1)
    with c2:
        # AJOUT APPORT VARIABLE
        apport = st.number_input("Votre Apport (€)", value=30000, step=1000, format="%d")
        montant_emprunte_final = montant_projet_input - apport
        revenus_totaux = 0
        taux_endettement_choisi = 0 # Non utilisé dans ce mode
else:
    st.caption("Ajustez vos revenus et votre taux d'endettement souhaité")
    c_rev1, c_rev2 = st.columns(2)
    with c_rev1:
        revenu_1 = st.number_input("Revenus nets mensuels (Emprunteur 1)", value=2500, step=100, format="%d")
    with c_rev2:
        revenu_2 = st.number_input("Revenus nets mensuels (Conjoint)", value=0, step=100, format="%d")
    
    # AJOUT APPORT ET TAUX ENDETTEMENT
    c_fin1, c_fin2 = st.columns(2)
    with c_fin1:
        apport = st.number_input("Votre Apport (€)", value=30000, step=1000, format="%d")
    with c_fin2:
        # AJOUT CURSEUR TAUX ENDETTEMENT
        taux_endettement_choisi = st.slider("Taux d'endettement max (%)", 30, 40, 35, 1, help="Généralement 35% assurance comprise")

    duree_annees = st.slider("Durée souhaitée (années)", 7, 30, 20, 1)
    
    revenus_totaux = revenu_1 + revenu_2
    # Calcul dynamique selon le curseur
    mensualite_cible_capacite = revenus_totaux * (taux_endettement_choisi / 100)

st.markdown("### 2. Conditions du Marché")
c3, c4 = st.columns(2)
with c3:
    taux_nominal = st.number_input("Taux d'intérêt nominal (%)", value=3.60, step=0.05, format="%.2f")
with c4:
    taux_assurance = st.number_input("Taux d'assurance moyen (%)", value=0.34, step=0.01, format="%.2f")

# --- CALCULS ---
tm = taux_nominal / 100 / 12
t_ass_mensuel = taux_assurance / 100 / 12
nb_mois = duree_annees * 12

if mode_calcul == "🎯 Calculer une Mensualité":
    if montant_emprunte_final > 0:
        mensualite_hors_ass = montant_emprunte_final * (tm * (1 + tm)**nb_mois) / ((1 + tm)**nb_mois - 1)
        mensualite_ass = montant_emprunte_final * t_ass_mensuel
        mensualite_cc_finale = mensualite_hors_ass + mensualite_ass
    else:
        mensualite_cc_finale, mensualite_ass, montant_emprunte_final = 0, 0, 0
else:
    if mensualite_cible_capacite > 0:
        facteur_amortissement = (tm * (1 + tm)**nb_mois) / ((1 + tm)**nb_mois - 1) if tm > 0 else 1/nb_mois
        facteur_total = facteur_amortissement + t_ass_mensuel
        montant_emprunte_final = mensualite_cible_capacite / facteur_total
        mensualite_cc_finale = mensualite_cible_capacite
        mensualite_ass = montant_emprunte_final * t_ass_mensuel
    else:
        mensualite_cc_finale, mensualite_ass, montant_emprunte_final = 0, 0, 0

cout_total_credit = (mensualite_cc_finale * nb_mois) - montant_emprunte_final

# --- RÉSULTATS INTELLIGENTS (AFFICHAGE CONDITIONNEL) ---
st.write("")
st.write("")

if mode_calcul == " Calculer une Mensualité":
    # MODE 1 : ON AFFICHE LA MENSUALITÉ EN GROS
    st.markdown(f"""
    <div class="main-result-card">
        <div class="result-label-big">Votre Mensualité Estimée (Assurance incluse)</div>
        <div class="result-val-big">{fmt(mensualite_cc_finale)} € <span style="font-size:1.5rem;">/ mois</span></div>
        <div class="result-sub-val">
            Pour un emprunt de {fmt(montant_emprunte_final)} € (Apport déduit)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    phrase_synthese = f"💡 **Synthèse du coût :** Pour un projet de **{fmt(montant_projet_input)} €** avec **{fmt(apport)} €** d'apport, vous empruntez **{fmt(montant_emprunte_final)} €**. Le coût total du crédit est estimé à **{fmt(cout_total_credit)} €**."

else:
    # MODE 2 : ON AFFICHE LA CAPACITÉ D'EMPRUNT EN GROS
    st.markdown(f"""
    <div class="main-result-card">
        <div class="result-label-big">Montant Maximum Empruntable</div>
        <div class="result-val-big">{fmt(montant_emprunte_final)} €</div>
        <div class="result-sub-val">
            Mensualité max : {fmt(mensualite_cc_finale)} €/mois ({taux_endettement_choisi}% endettement)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    budget_total = montant_emprunte_final + apport
    phrase_synthese = f"💡 **Enveloppe Globale :** En ajoutant votre apport de **{fmt(apport)} €** à ce crédit, votre budget d'achat total (FAI) s'élève à environ **{fmt(budget_total)} €**."

# Encart central de synthèse
st.info(phrase_synthese)

# --- FORMULAIRE DE CONTACT ---
st.write("")
st.write("")
st.markdown("###  Concrétisez votre projet avec PATRIM")

with st.container(border=True):
    st.markdown("#### Demander une étude personnalisée")
    st.markdown("Sélectionnez le type de projet pour pré-qualifier votre demande :")
    
    col_check1, col_check2, col_check3 = st.columns(3)
    with col_check1: type_rp = st.checkbox("Résidence Principale")
    with col_check2: type_inv = st.checkbox("Investissement Locatif")
    with col_check3: type_rs = st.checkbox("Résidence Secondaire")
    
    # Génération du mail
    sujet_mail = f"Demande étude financement - Projet ~{fmt(montant_emprunte_final)}€"
    intro_mail = ""
    
    if mode_calcul == " Ma Capacité d'emprunt":
        intro_mail = f"Capacité calculée sur revenus de {fmt(revenus_totaux)} €/mois avec {taux_endettement_choisi}% d'endettement.\n"
    else:
        intro_mail = f"Calcul de mensualité pour un projet global de {fmt(montant_projet_input)} €.\n"

    corps_mail = f"""Bonjour Quentin,
    
Je souhaite affiner la simulation effectuée sur votre site :

--- SYNTHÈSE ---
{intro_mail}
- Montant financé (Crédit) : {fmt(montant_emprunte_final)} €
- Apport personnel : {fmt(apport)} €
- Durée : {duree_annees} ans
- Mensualité ciblée (AI) : {fmt(mensualite_cc_finale)} €/mois

--- PROJET ---
Type : {'[X] RP ' if type_rp else ''}{'[X] Locatif ' if type_inv else ''}{'[X] Secondaire ' if type_rs else ''}

Merci de me recontacter pour une étude approfondie.

Cordialement,"""
    
    mailto_link = f"mailto:quentin.delsol@patrim.fr?subject={urllib.parse.quote(sujet_mail)}&body={urllib.parse.quote(corps_mail)}"
    
    st.markdown(f"""
        <a href="{mailto_link}" class="contact-btn">
            📩 Envoyer ma simulation à Quentin Delsol
        </a>
        <p style="text-align:center; margin-top:15px; color:#888 !important; font-size:0.8rem;">
            En cliquant, votre application de messagerie s'ouvrira automatiquement.
        </p>
    """, unsafe_allow_html=True)
