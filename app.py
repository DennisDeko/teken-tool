import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- DATABASE STANDAARD MATEN ---
steen_maten = {
    "Vrij invoeren": (210, 100, 50),
    "Waalformaat": (210, 100, 50),
    "Dikformaat / waaldikformaat": (210, 100, 65),
    "Brabantse steen": (180, 88, 53),
    "Deens formaat": (228, 108, 54),
    "Dordtse steen": (180, 88, 43),
    "Dubbel waalformaat": (210, 100, 110),
    "Dunnformat (DF)": (240, 115, 52),
    "Engels formaat": (210, 102.5, 65),
    "Euroformat": (188, 90, 88),
    "F52": (230, 110, 57),
    "Friese drieling": (184, 80, 40),
    "Friese mop": (217, 103, 45),
    "Goudse steen": (155, 72, 53),
    "Groninger steen": (240, 120, 60),
    "Hilversums formaat": (240, 90, 40),
    "IJsselformaat": (160, 78, 41),
    "Juffertje": (175, 82, 40),
    "Kathedraal I": (240, 115, 65),
    "Kathedraal II": (270, 105, 55),
    "Klampmuur-dikformaat": (100, 65, 210),
    "Kloostermop I": (280, 105, 80),
    "Kloostermop II": (320, 130, 80),
    "Lilliput I": (160, 75, 35),
    "Lilliput II": (150, 70, 30),
    "Limburgse steen": (240, 120, 65),
    "Moduul 190-140-90": (190, 140, 90),
    "Moduul 190-90-40": (190, 90, 40),
    "Moduul 190-90-50": (190, 90, 50),
    "Moduul 190-90-90": (190, 90, 90),
    "Moduul 240-90-90": (240, 90, 90),
    "Moduul 290-115-190": (290, 115, 190),
    "Moduul 290-115-90": (290, 115, 90),
    "Moduul 290-90-190": (290, 90, 190),
    "Moduul 290-90-90": (290, 90, 90),
    "Normalformat (NF)": (240, 115, 71),
    "Oldenburgerformat (OF)": (210, 105, 52),
    "Reichsformat (RF)": (240, 115, 61),
    "Rijnformaat": (180, 87, 41),
    "Romeins formaat": (240, 115, 42),
    "Utrechts plat": (215, 102, 38),
    "Vechtformaat": (210, 100, 40),
    "Verblender (2DF)": (240, 115, 113)
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
# 1. Selectie standaardmaten (NU BOVENAAN)
with st.sidebar.expander("Snelkeuze Steenformaat", expanded=True):
    keuze_naam = st.selectbox("Kies standaard maat", list(steen_maten.keys()))
    std_l, std_b, std_h = steen_maten[keuze_naam]

vorm_type = st.sidebar.selectbox("Type product", ["Steen", "Hoek"])
zaag_dikte = st.sidebar.slider("Zaagblad dikte (mm)", 0.0, 5.0, 3.0)

# 2. Afmetingen (worden gevuld vanuit selectie)
with st.sidebar.expander("Afmetingen Aanpassen", expanded=True):
    l1 = st.number_input("Lengte L1 (mm)", value=float(std_l))
    l2 = st.number_input("Breedte/Lengte L2 (mm)", value=float(std_b))
    h = st.number_input("Hoogte H (mm)", value=float(std_h))
    
    if vorm_type == "Hoek":
        dikte = st.number_input("Dikte D (mm)", value=23.0)
        grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        vlak_indices = [[0,1,2,3,4,5], [6,7,8,9,10,11], [0,1,7,6], [1,2,8,7], [2,3,9,8], [3,4,10,9], [4,5,11,10], [5,0,6,11]]
    else:
        dikte = 0.0
        grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]

# 3. Zaaglijnen
with st.sidebar.expander("Zaaglijnen (Rood)", expanded=False):
    ax = st.slider("Aantal X-snedes", 0, 5, 0)
    pos_x = [st.number_input(f"X{i+1}", value=23.0 if i==0 else l1-23, key=f"x{i}") for i in range(ax)]
    ay = st.slider("Aantal Y-snedes", 0, 5, 0)
    pos_y = [st.number_input(f"Y{i+1}", value=23.0 if i==0 else l2-23, key=f"y{i}") for i in range(ay)]

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    ax1.add_patch(plt.Polygon(grond_poly, facecolor='lightgray', alpha=0.3, edgecolor='black'))

    for i, px in enumerate(pos_x):
        y_m = l2 if (vorm_type=="Steen" or px<=dikte) else dikte
        ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_m, facecolor='red', alpha=0.6))
        txt = f"X{i+1}: {int(px)}" if px <= l1/2 else f"X{i+1}: {int(px)} ({int(l1-px)} v. R)"
        ax1.text(px, y_m+5, txt, color='red', weight='bold', fontsize=8, ha='center')

    for i, py in enumerate(pos_y):
        x_m = l1 if (vorm_type=="Steen" or py<=dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py), x_m, zaag_dikte, facecolor='red', alpha=0.6))
        txt = f"Y{i+1}: {int(py)}" if py <= l2/2 else f"Y{i+1}: {int(py)} ({int(l2-py)} v. B)"
        ax1.text(x_m+5, py, txt, color='red', weight='bold', fontsize=8, va='center')

    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1, dpi=80)

with col2:
    st.subheader("3D Vlakken Preview")
    fig2 = plt.figure(); ax2 = fig2.add_subplot(111, projection='3d')
    v_3d = np.array([ [p[0],p[1],0] for p in grond_poly ] + [ [p[0],p[1],h] for p in grond_poly ])
    ax2.add_collection3d(Poly3DCollection([[v_3d[i] for i in idx] for idx in vlak_indices], facecolors='cyan', alpha=0.1, edgecolors='black'))

    for px in pos_x:
        y_top = l2 if (vorm_type=="Steen" or px<=dikte) else dikte
        vlak = [[px,0,0], [px+zaag_dikte,0,0], [px+zaag_dikte,y_top,h], [px,y_top,h]]
        ax2.add_collection3d(Poly3DCollection([vlak], facecolors='red', alpha=0.6))

    for py in pos_y:
        x_top = l1 if (vorm_type=="Steen" or py<=dikte) else dikte
        vlak = [[0,py,0], [x_top,py,0], [x_top,py+zaag_dikte,h], [0,py+zaag_dikte,h]]
        ax2.add_collection3d(Poly3DCollection([vlak], facecolors='red', alpha=0.6))

    lim = max(l1,l2,h)
    ax2.set_xlim(0, lim); ax2.set_ylim(0, lim); ax2.set_zlim(0, lim)
    ax2.view_init(elev=20, azim=-35); ax2.axis('off')
    st.pyplot(fig2, dpi=80)

# --- OVERZICHTSTABEL ---
st.divider()
st.subheader(f"📋 Werkinstructie: {keuze_naam}")
overzicht = {"Omschrijving": ["L1 (Lengte)", "L2 (Breedte)", "H (Hoogte)"], "Maat (mm)": [l1, l2, h]}
if vorm_type == "Hoek":
    overzicht["Omschrijving"].append("D (Dikte)")
    overzicht["Maat (mm)"].append(dikte)

st.table(pd.DataFrame(overzicht))
