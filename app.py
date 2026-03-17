import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- HIER VERVANGEN WE HET ICOON VOOR HET LOGO ---
# PAS DIT AAN: Plak hier de 'Raw' URL van je afbeelding op GitHub
LOGO_URL = "https://raw.githubusercontent.com/JOUW_GEBRUIKERSNAAM/mijn-maten-tool/main/deko-logo.png"

# Maak twee kolommen voor de kop: één voor het logo, één voor de tekst
col_logo, col_titel = st.columns([1, 4]) # Het logo krijgt 1/5 van de breedte

with col_logo:
    # We laden het logo. 'use_column_width=True' zorgt dat het mooi schaalt.
    try:
        st.image(LOGO_URL, use_column_width=True)
    except:
        # Als de URL niet werkt, laten we toch het liniaaltje zien als backup
        st.error("Logo kon niet worden geladen. Controleer de URL.")
        st.title("📏")

with col_titel:
    # De titel komt in de kolom ernaast
    st.title("Universele Maten Tool Pro")

st.divider()

# --- De rest van de code blijft hetzelfde ---

# 1. Kies het type vorm
vorm_type = st.sidebar.selectbox("Kies een vorm", ["Rechthoek / Balk", "L-Vorm"])

st.sidebar.divider()

# 2. Input op basis van keuze
if vorm_type == "Rechthoek / Balk":
    l1 = st.sidebar.number_input("Lengte (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Breedte (cm)", min_value=1.0, value=50.0)
    h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=40.0)
    dikte = 0.0
    grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
else:
    l1 = st.sidebar.number_input("Lengte Zijde 1 (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Lengte Zijde 2 (cm)", min_value=1.0, value=60.0)
    limiet = float(min(l1, l2))
    dikte = st.sidebar.number_input("Dikte (cm)", min_value=0.1, max_value=limiet, value=20.0)
    h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=30.0)
    grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
    vlak_indices = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]]

# --- Visualisatie ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Bovenaanzicht")
    fig1, ax1 = plt.subplots()
    omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='blue', linewidth=2)
    ax1.add_patch(omtrek)
    m = max(l1, l2) + 5
    ax1.set_xlim(-5, m); ax1.set_ylim(-5, m); ax1.set_aspect('equal'); ax1.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig1)

with col2:
    st.subheader("3D Model")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    v = []
    for p in grond_poly: v.append([p[0], p[1], 0])
    for p in grond_poly: v.append([p[0], p[1], h])
    v = np.array(v)
    vlakken = [[v[i] for i in idx] for idx in vlak_indices]
    k = 'cyan' if vorm_type == "Rechthoek / Balk" else 'orange'
    poly3d = Poly3DCollection(vlakken, facecolors=k, linewidths=1, edgecolors='blue', alpha=.4)
    ax2.add_collection3d(poly3d)
    d = max(l1, l2, h)
    ax2.set_xlim(0, d); ax2.set_ylim(0, d); ax2.set_zlim(0, d)
    ax2.grid(False); ax2.xaxis.pane.fill = ax2.yaxis.pane.fill = ax2.zaxis.pane.fill = False
    st.pyplot(fig2)

# --- Alleen maten overzicht ---
st.divider()
st.subheader("📋 Ingevoerde Maten")

data = {
    "Omschrijving": ["Lengte / Zijde 1", "Breedte / Zijde 2", "Hoogte", "Materiaaldikte"],
    "Maat (cm)": [f"{l1} cm", f"{l2} cm", f"{h} cm", f"{dikte} cm" if dikte > 0 else "N.v.t."]
}
df = pd.DataFrame(data)
st.table(df)
