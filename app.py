import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Transformatie Tool", layout="wide")

# --- DATABASE ---
steen_maten = {
    "Vrij invoeren": (210, 100, 50),
    "Waalformaat": (210, 100, 50),
    "Dikformaat": (210, 100, 65),
    "Vechtformaat": (210, 100, 40),
    "Hilversums formaat": (240, 90, 40),
    # ... overige maten uit vorige lijst blijven behouden
}

transformaties = [
    "Strippen (2-zijdig)", "Strippen (1-zijdig)", "Sparren", "Afkorten", 
    "Hoeken", "Hoeken plat (kopbakje)", "Koppen", "Kopstrippen", 
    "Bakjes", "Zolen", "Lomkop", "Romkop", "Kimstenen"
]

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuratie")
    
    with st.expander("1. Basis Steen", expanded=True):
        keuze_naam = st.selectbox("Kies standaard maat", list(steen_maten.keys()))
        std_l, std_b, std_h = steen_maten[keuze_naam]
        l1 = st.number_input("Lengte L1 (mm)", value=float(std_l))
        l2 = st.number_input("Breedte L2 (mm)", value=float(std_b))
        h = st.number_input("Hoogte H (mm)", value=float(std_h))

    with st.expander("2. Transformatie", expanded=True):
        type_trans = st.selectbox("Kies bewerking", transformaties)
        # Standaard 23mm, maar nu overal aanpasbaar
        bewerkings_maat = st.number_input("Bewerkingsmaat (mm)", min_value=1.0, value=23.0, help="Bijv. stripdikte of zaagafstand")
        zaag_dikte = st.slider("Zaagblad dikte (mm)", 0.0, 5.0, 3.0)

    # Automatische logica voor zaaglijnen op basis van type
    pos_x = []
    pos_y = []
    
    if "Strippen" in type_trans or "Zolen" in type_trans:
        pos_y = [bewerkings_maat]
        if "2-zijdig" in type_trans:
            pos_y.append(l2 - bewerkings_maat - zaag_dikte)
            
    elif "Afkorten" in type_trans:
        pos_x = [st.number_input("Afkortmaat X (mm)", value=l1/2)]

# --- VISUALISATIE (2D) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"2D Zaagplan: {type_trans}")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    
    # Steen tekenen
    omtrek = [[0,0], [l1,0], [l1,l2], [0,l2]]
    ax1.add_patch(plt.Polygon(omtrek, facecolor='lightgray', alpha=0.3, edgecolor='black'))

    # Zaaglijnen tekenen
    for px in pos_x:
        ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, l2, color='red', alpha=0.7))
    for py in pos_y:
        ax1.add_patch(plt.Rectangle((0, py), l1, zaag_dikte, color='red', alpha=0.7))

    ax1.set_xlim(-10, l1+20); ax1.set_ylim(-10, l2+20)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1, dpi=80)

# --- 3D MODEL ---
with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(); ax2 = fig2.add_subplot(111, projection='3d')
    # Basis blok genereren
    z = np.array([[0,0,0], [l1,0,0], [l1,l2,0], [0,l2,0], [0,0,h], [l1,0,h], [l1,l2,h], [0,l2,h]])
    vlakken = [[z[0],z[1],z[2],z[3]], [z[4],z[5],z[6],z[7]], [z[0],z[1],z[5],z[4]], [z[1],z[2],z[6],z[5]], [z[2],z[3],z[7],z[6]], [z[3],z[0],z[4],z[7]]]
    ax2.add_collection3d(Poly3DCollection(vlakken, facecolors='cyan', alpha=0.1, edgecolors='black'))

    # Zaagvlakken in 3D
    for py in pos_y:
        zv = [[0,py,0], [l1,py,0], [l1,py,h], [0,py,h]]
        ax2.add_collection3d(Poly3DCollection([zv], facecolors='red', alpha=0.5))

    ax2.set_xlim(0, max(l1,l2,h)); ax2.set_ylim(0, max(l1,l2,h)); ax2.set_zlim(0, max(l1,l2,h))
    ax2.view_init(elev=20, azim=-35); ax2.axis('off')
    st.pyplot(fig2, dpi=80)
