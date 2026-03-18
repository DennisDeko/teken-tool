import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Maatwerk Editor Pro", layout="wide")

# --- DATABASE STANDAARD MATEN ---
steen_maten = {
    "Waalformaat": (210, 100, 50),
    "Dikformaat / waaldikformaat": (210, 100, 65),
    "Vechtformaat": (210, 100, 40),
    "Hilversums formaat": (240, 90, 40),
    "Brabantse steen": (180, 88, 53),
    "Deens formaat": (228, 108, 54),
    "Dordtse steen": (180, 88, 43),
    "Dubbel waalformaat": (210, 100, 110),
    "Euroformat": (188, 90, 88),
    "Groninger steen": (240, 120, 60),
    "IJsselformaat": (160, 78, 41),
    "Kloostermop I": (280, 105, 80),
    "Lilliput I": (160, 75, 35),
    "Vrij invoeren": (210, 100, 50)
}

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_l, col_r = st.columns([1, 3])
with col_l:
    st.image(LOGO_URL, width=180)
with col_r:
    st.title("DEKO Maatwerk Editor Pro")

st.divider()

# --- SIDEBAR ---
with st.sidebar:
    with st.expander("Snelkeuze Steenformaat", expanded=True):
        keuze_naam = st.selectbox("Kies standaard maat", list(steen_maten.keys()))
        std_l, std_b, std_h = steen_maten[keuze_naam]

    st.header("Transformatie Instellingen")
    transformatie = st.selectbox("Type", ["Strippen", "Koppen", "Afkorten"])
    aantal_zijden = st.radio("Aantal zijden", ["Enkelzijdig", "Dubbelzijdig"])
    
    zaag_dikte = st.slider("Zaagblad dikte (mm)", 0.0, 5.0, 3.0)

    with st.expander("Afmetingen Basissteen", expanded=True):
        l1 = st.number_input("Lengte L1 (mm)", value=float(std_l))
        l2 = st.number_input("Breedte L2 (mm)", value=float(std_b))
        h = st.number_input("Hoogte H (mm)", value=float(std_h))

    with st.expander("Bewerkingsmaten", expanded=True):
        dikte_strip = st.number_input("Dikte van de strip (mm)", value=23.0, min_value=1.0)

# --- LOGICA VOOR STRIPPEN EN KOPPEN ---
product_vlakken_2d = [] # [(x, y, w, h)]
zaaglijnen_2d = []

if transformatie == "Strippen":
    # Strip 1 (Onderzijde)
    product_vlakken_2d.append((0, 0, l1, dikte_strip))
    zaaglijnen_2d.append((0, dikte_strip, l1, zaag_dikte))
    
    if aantal_zijden == "Dubbelzijdig":
        # Strip 2 (Bovenzijde)
        product_vlakken_2d.append((0, l2 - dikte_strip, l1, dikte_strip))
        zaaglijnen_2d.append((0, l2 - dikte_strip - zaag_dikte, l1, zaag_dikte))

elif transformatie == "Koppen":
    # Kop 1 (Links)
    product_vlakken_2d.append((0, 0, dikte_strip, l2))
    zaaglijnen_2d.append((dikte_strip, 0, zaag_dikte, l2))
    
    if aantal_zijden == "Dubbelzijdig":
        # Kop 2 (Rechts)
        product_vlakken_2d.append((l1 - dikte_strip, 0, dikte_strip, l2))
        zaaglijnen_2d.append((l1 - dikte_strip - zaag_dikte, 0, zaag_dikte, l2))

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    # Basissteen (grijs restant)
    ax1.add_patch(plt.Rectangle((0, 0), l1, l2, facecolor='lightgray', alpha=0.3, edgecolor='black', linestyle='--'))

    # De Blauwe Strippen/Koppen
    for (x, y, w, hb) in product_vlakken_2d:
        ax1.add_patch(plt.Rectangle((x, y), w, hb, facecolor='cyan', alpha=0.7, edgecolor='blue', label='Strip'))

    # De Rode Zaaglijnen
    for (zx, zy, zw, zh) in zaaglijnen_2d:
        ax1.add_patch(plt.Rectangle((zx, zy), zw, zh, facecolor='red', alpha=0.8))

    ax1.set_xlim(-10, l1 + 20); ax1.set_ylim(-10, l2 + 20)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1, dpi=80)

with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(); ax2 = fig2.add_subplot(111, projection='3d')
    
    # Basis blok (spookvorm)
    z = np.array([[0,0,0], [l1,0,0], [l1,l2,0], [0,l2,0], [0,0,h], [l1,0,h], [l1,l2,h], [0,l2,h]])
    vlak_indices = [[0,1,2,3], [4,5,6,7], [0,1,5,4], [1,2,6,5], [2,3,7,6], [3,0,4,7]]
    ax2.add_collection3d(Poly3DCollection([[z[i] for i in idx] for idx in vlak_indices], facecolors='gray', alpha=0.05, edgecolors='black'))

    # Blauwe Strippen in 3D
    for (x, y, w, hb) in product_vlakken_2d:
        sz = np.array([[x,y,0], [x+w,y,0], [x+w,y+hb,0], [x,y+hb,0], [x,y,h], [x+w,y,h], [x+w,y+hb,h], [x,y+hb,h]])
        s_vlakken = [[0,1,2,3], [4,5,6,7], [0,1,5,4], [1,2,6,5], [2,3,7,6], [3,0,4,7]]
        ax2.add_collection3d(Poly3DCollection([[sz[i] for i in idx] for idx in s_vlakken], facecolors='cyan', alpha=0.6, edgecolors='blue'))

    ax2.set_xlim(0, max(l1,l2,h)); ax2.set_ylim(0, max(l1,l2,h)); ax2.set_zlim(0, max(l1,l2,h))
    ax2.view_init(elev=20, azim=-35); ax2.axis('off')
    st.pyplot(fig2, dpi=80)

# --- OVERZICHTSTABEL ---
st.divider()
st.subheader("📋 Productiedetails")
df_data = {
    "Onderdeel": ["Gekozen Steen", "Bewerking", "Strip Dikte", "Aantal Strippen"],
    "Waarde": [keuze_naam, transformatie, f"{dikte_strip} mm", "2" if aantal_zijden == "Dubbelzijdig" else "1"]
}
st.table(pd.DataFrame(df_data))
