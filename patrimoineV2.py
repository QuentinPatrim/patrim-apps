import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Cabinet Stratégie AI", layout="wide", page_icon="🏛️")

# --- INITIALISATION SESSION STATE ---
if 'biens_immo' not in st.session_state: st.session_state.biens_immo = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

# --- FONCTIONS UTILITAIRES ---
def formater_euro(montant):
    return f"{montant:,.0f} €".replace(",", " ")

def calculer_tmi(net_annuel_foyer, parts):
    revenu_imposable = net_annuel_foyer * 0.9 
    quotient = revenu_imposable / parts if parts > 0 else 0
    if quotient <= 11294: return 0
    elif quotient <= 28797: return 11
    elif quotient <= 82341: return 30
    elif quotient <= 177106: return 41
    else: return 45

# --- FONCTION IA LOCALE SÉCURISÉE ---
def get_ai_response(prompt_text, context_data):
    """Interroge le modèle local Ollama (Mistral) avec sécurité anti-crash"""
    try:
        # On importe ici pour éviter le crash si la librairie manque
        from langchain_community.llms import Ollama
        
        # Test de connexion
        llm = Ollama(model="mistral")
        
        context_str = f"""
        Tu es un expert senior en gestion de patrimoine.
        Données client :
        - Profil : {context_data['age']} ans, {context_data['statut']}, {context_data['nb_enfants']} enfants.
        - Revenus : {context_data['revenus_annuels']/12:.0f} €/mois. TMI : {context_data['tmi']}%.
        - Patrimoine Net : {context_data['patrimoine_net']} €.
        - Liquidités : {context_data['finance_cash']} €.
        - Immobilier : {len(context_data['immo_liste'])} biens.
        
        Réponds de manière professionnelle et concise.
        """
        full_prompt = f"{context_str}\n\nQuestion : {prompt_text}"
        return llm.invoke(full_prompt)
        
    except ImportError:
        return "⚠️ Erreur : La librairie 'langchain-community' n'est pas installée. Tapez 'pip install langchain-community' dans le terminal."
    except Exception as e:
        return f"⚠️ L'IA n'est pas disponible. Assurez-vous d'avoir installé Ollama sur ollama.com et lancé l'application. (Erreur technique: {e})"

# --- MOTEUR ANALYSE LOGIQUE ---
def generer_audit_expert(data, biens_immo):
    audit = {"score_global": 50, "alertes": [], "conseils": [], "synthese": []}
    
    mois_securite = data['finance_cash'] / (data['depenses_annuelles']/12) if data['depenses_annuelles'] > 0 else 0
    
    if mois_securite < 3:
        audit["alertes"].append(f"Liquidité critique ({mois_securite:.1f} mois).")
        audit["score_global"] -= 20
    elif mois_securite > 10:
        audit["conseils"].append("Excédent de trésorerie à investir.")
        
    if data['taux_endettement'] > 35:
        audit["alertes"].append(f"Endettement élevé ({data['taux_endettement']:.1f}%).")
        audit["score_global"] -= 10
        
    if data['tmi'] >= 30 and data['finance_pea'] == 0:
        audit["conseils"].append("Ouvrir un PEA pour la capitalisation à fiscalité douce.")
        
    audit["score_global"] = max(0, min(100, audit["score_global"]))
    return audit

# --- INTERFACE ---
st.sidebar.header("Dossier Client")

# 1. SAISIE PROFIL (CORRIGÉ ICI : Valeur défaut 40 au lieu de 0)
with st.sidebar.expander("👤 Profil & Fiscalité", expanded=True):
    age = st.number_input("Âge", 18, 99, 40) # <-- CORRECTION DE L'ERREUR STREAMLIT
    statut = st.radio("Situation", ["Célibataire", "Marié/Pacsé"], horizontal=True)
    nb_enfants = st.number_input("Enfants", 0, 10, 2)
    parts = 1 if statut == "Célibataire" else 2
    if nb_enfants <= 2: parts += nb_enfants * 0.5
    else: parts += nb_enfants - 1
    revenus_mensuels = st.number_input("Revenus Nets Foyer / mois", 0, 50000, 4000, step=100)
    depenses_annuelles = st.number_input("Dépenses Annuelles", 0, 200000, 30000, step=1000)

# 2. SAISIE FINANCES
st.sidebar.header("💰 Actifs Financiers")
with st.sidebar.expander("Placements", expanded=False):
    fin_cash = st.number_input("Liquidités (Livrets)", 0, 1000000, 20000, step=1000)
    fin_pea = st.number_input("PEA", 0, 500000, 5000, step=1000)
    fin_cto = st.number_input("CTO", 0, 1000000, 0, step=1000)
    fin_av = st.number_input("Assurance Vie", 0, 2000000, 10000, step=1000)
    fin_crypto = st.number_input("Crypto", 0, 1000000, 0, step=1000)

# 3. SAISIE IMMO
st.sidebar.header("🧱 Parc Immobilier")
with st.sidebar.expander("Gérer les biens", expanded=False):
    with st.form("add_immo"):
        type_b = st.selectbox("Type", ["RP", "Locatif", "Secondaire", "Parking", "SCPI"])
        val_b = st.number_input("Valeur", 0, 5000000, 200000, step=5000)
        cred_b = st.number_input("Crédit Restant", 0, 5000000, 150000, step=5000)
        mens_b = st.number_input("Mensualité", 0, 10000, 800, step=50)
        loy_b = st.number_input("Loyer (si locatif)", 0, 10000, 0, step=50)
        if st.form_submit_button("Ajouter"):
            st.session_state.biens_immo.append({"type": type_b, "valeur": val_b, "credit": cred_b, "mensualite": mens_b, "loyer": loy_b})
            st.success("Bien ajouté")

# --- CONSOLIDATION ---
total_immo = sum(b['valeur'] for b in st.session_state.biens_immo)
total_dette = sum(b['credit'] for b in st.session_state.biens_immo)
total_mens = sum(b['mensualite'] for b in st.session_state.biens_immo)
total_fin = fin_cash + fin_pea + fin_cto + fin_av + fin_crypto
patrimoine_net = (total_fin + total_immo) - total_dette
taux_endettement = (total_mens / revenus_mensuels * 100) if revenus_mensuels > 0 else 0
tmi = calculer_tmi(revenus_mensuels*12, parts)

context_data = {
    "age": age, "statut": statut, "nb_enfants": nb_enfants,
    "revenus_annuels": revenus_mensuels*12, "tmi": tmi,
    "patrimoine_net": patrimoine_net,
    "finance_cash": fin_cash, "finance_total": total_fin, "finance_pea": fin_pea,
    "immo_liste": st.session_state.biens_immo,
    "depenses_annuelles": depenses_annuelles, "taux_endettement": taux_endettement
}

audit = generer_audit_expert(context_data, st.session_state.biens_immo)

# --- VISUEL PRINCIPAL ---
st.title("🏛️ Cabinet Stratégie & IA")

k1, k2, k3 = st.columns(3)
k1.metric("Patrimoine Net", formater_euro(patrimoine_net))
k2.metric("Score Santé", f"{audit['score_global']}/100")
k3.metric("TMI", f"{tmi}%")

tabs = st.tabs(["📊 Diagnostic", "🤖 Assistant IA", "🧱 Immo & Alloc"])

with tabs[0]:
    st.subheader("Analyse Synthétique")
    c1, c2 = st.columns(2)
    with c1:
        if audit['alertes']: st.error("⚠️ Vigilance : " + ", ".join(audit['alertes']))
        if audit['conseils']: st.info("💡 Conseils : " + ", ".join(audit['conseils']))
    
    with c2:
        st.write("### 🧠 Analyse Approfondie IA")
        if st.button("Lancer l'Analyse IA"):
            with st.spinner("Analyse via Ollama Local..."):
                reponse_ia = get_ai_response("Fais une analyse critique et propose 3 actions.", context_data)
                st.markdown(reponse_ia)

with tabs[1]:
    st.subheader("💬 Discussion avec l'Expert IA")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Posez votre question..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.spinner("Réflexion..."):
            response = get_ai_response(prompt, context_data)
            
        st.chat_message("assistant").markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

with tabs[2]:
    st.subheader("Allocation d'Actifs")
    df_assets = pd.DataFrame({
        'Actif': ['Cash', 'PEA', 'CTO', 'Assurance Vie', 'Crypto', 'Immobilier'],
        'Valeur': [fin_cash, fin_pea, fin_cto, fin_av, fin_crypto, total_immo]
    })
    if patrimoine_net > 0:
        fig = px.pie(df_assets, values='Valeur', names='Actif', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.biens_immo:
        st.write("#### Détail Immo")
        st.dataframe(pd.DataFrame(st.session_state.biens_immo))
