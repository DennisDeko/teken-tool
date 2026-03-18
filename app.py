import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Transformaties - 2 Strippen", layout="wide")

# --- DATABASE STEENMATEN ---
steen_maten = {
    "Vrij invoeren": (210, 100, 50),
    "Waalformaat": (210, 100, 50),
    "Dikformaat": (210, 100, 65),
    "Vechtformaat": (210, 100, 40),
    "Hilversums formaat": (240, 90, 40),
    "Moduul 190-90-50": (190, 90, 50),
    "Kloostermop I": (280, 105, 80)
}

transformaties = [
    "Strippen (2-zijdig)", "Strippen (1-zijdig)", "Sparren", "Afkorten", 
    "Hoeken", "Hoeken plat (kopbakje)", "Koppen", "Kopstrippen", 
    "Bakjes", "Zolen", "Lomkop", "Romkop", "Kimstenen"
]

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_l, col_r = st.columns([1, 3])
with col_l:
    st.image(LOGO_URL, width=200)
with col_r:
    st.title("DEKO 3D Product Generator")

st.divider()

# --- SIDEBAR LOGICA ---
with st.sidebar:
    st.header("1. Basis Steen")
    keuze_naam = st.selectbox("Kies standaard maat", list(steen_maten.keys()))
    std_l, std_b, std_h = steen_maten[keuze_naam]
    base_L = st.number_input("Oorspronkelijke Lengte", value=float(std_l))
    base_B = st.number_input("Oorspronkelijke Breedte", value=float(std_b))
    base_H = st.number_input("Oorspronkelijke Hoogte", value=float(std_h))
    zaag_dikte = st.slider("Zaagblad dikte (mm)", 0.0, 5.0, 3.0)

    st.header("2. Transformatie & Maten")
    type_trans = st.selectbox("Kies bewerking", transformaties)
    
    # Dynamische Variabelen
    A = st.number_input("A: Lengte product (mm)", value=base_L)
    B = st.number_input("B: Breedte/Diepte totaal (mm)", value=base_B)
    C = st.number_input("C: Hoogte product (mm)", value=base_H)
    
    vorm_categorie = "Blok"
    D, E, X = 0.0, 0.0, 0.0

    if type_trans in ["Hoeken", "Hoeken plat (kopbakje)", "Lomkop", "Romkop"]:
        vorm_categorie = "L-Vorm"
        D = st.number_input("D: Dikte strek (mm)", value=23.0)
        E = st.number_input("E: Dikte kop (mm)", value=23.0)
    elif type_trans in ["Bakjes", "Kop bak", "Zolen"]:
        vorm_categorie = "U-Vorm"
        D = st.number_input("D: Dikte voorzijde (mm)", value=23.0)
        E = st.number_input("E: Dikte zijwanden (mm)", value=23.0)
    elif "Strippen" in type_trans or type_trans in ["Kopstrippen", "Kimstenen"]:
        vorm_categorie = "Blok"
        D = st.number_input("D: Strip dikte (mm)", value=23.0)
    elif type_trans == "Afkorten":
        vorm_categorie = "Blok"
        X = st.number_input("X: Afkortmaat (mm)", value=base_L / 2)
        A = X

# --- 3D GEOMETRIE ENGINE ---
def genereer_3d_vlakken(profiel_2d, hoogte_c, z_offset=0):
    vlakken = []
    n = len(profiel_2d)
    vlakken.append([[p[0], p[1], z_offset] for p in profiel_2d])
    vlakken.append([[p[0], p[1], hoogte_c + z_offset] for p in profiel_2d])
    for i in range(n):
        p1, p2 = profiel_2d[i], profiel_2d[(i+1)%n]
        vlakken.append([[p1[0], p1[1], z_offset], [p2[0], p2[1], z_offset], 
                        [p2[0], p2[1], hoogte_c + z_offset], [p1[0], p1[1], hoogte_c + z_offset]])
    return vlakken

# LOGICA VOOR 2 STRIPPEN
producten_lijst = [] # Lijst met verschillende 3D onderdelen

if type_trans == "Strippen (2-zijdig)":
    # Strip 1 (Onderzijde)
    profiel1 = [(0,0), (A,0), (A,D), (0,D)]
    producten_lijst.append(genereer_3d_vlakken(profiel1, C))
    # Strip 2 (Bovenzijde)
    profiel2 = [(0, base_B - D), (A, base_B - D), (A, base_B), (0, base_B)]
    producten_lijst.append(genereer_3d_vlakken(profiel2, C))
    hoofd_profiel = profiel1 # Voor 2D preview
elif type_trans == "Strippen (1-zijdig)":
    profiel = [(0,0), (A,0), (A,D), (0,D)]
    producten_lijst.append(genereer_3d_vlakken(profiel, C))
    hoofd_profiel = profiel
elif vorm_categorie == "L-Vorm":
    profiel = [(0,0), (A,0), (A,D), (E,D), (E,B), (0,B)]
    producten_lijst.append(genereer_3d_vlakken(profiel, C))
    hoofd_profiel = profiel
elif vorm_categorie == "U-Vorm":
    profiel = [(0,0), (A,0), (A,B), (A-E,B), (A-E,D), (E,D), (E,B), (0,B)]
    producten_lijst.append(genereer_3d_vlakken(profiel, C))
    hoofd_profiel = profiel
else:
    profiel = [(0,0), (A,0), (A,B), (0,B)]
    producten_lijst.append(genereer_3d_vlakken(profiel, C))
    hoofd_profiel = profiel

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"2D Profiel (Top View)")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    basis_poly = plt.Polygon([(0,0), (base_L,0), (base_L,base_B), (0,base_B)], facecolor='gray', alpha=0.1, edgecolor='black', linestyle='--')
    ax1.add_patch(basis_poly)

    if type_trans == "Strippen (2-zijdig)":
        # Teken beide strips in 2D
        ax1.add_patch(plt.Polygon([(0,0), (A,0), (A,D), (0,D)], facecolor='cyan', alpha=0.6, edgecolor='blue', linewidth=2))
        ax1.add_patch(plt.Polygon([(0, base_B - D), (A, base_B - D), (A, base_B), (0, base_B)], facecolor='cyan', alpha=0.6, edgecolor='blue', linewidth=2))
    else:
        ax1.add_patch(plt.Polygon(hoofd_profiel, facecolor='cyan', alpha=0.6, edgecolor='blue', linewidth=2))

    ax1.set_xlim(-20, base_L + 40); ax1.set_ylim(-20, base_B + 40)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1, dpi=80)

with col2:
    st.subheader("3D Product Render")
    fig2 = plt.figure(figsize=(6, 5)); ax2 = fig2.add_subplot(111, projection='3d')
    z_box = np.array([[0,0,0], [base_L,0,0], [base_L,base_B,0], [0,base_B,0], [0,0,base_H], [base_L,0,base_H], [base_L,base_B,base_H], [0,base_B,base_H]])
    basis_vlakken = [[z_box[0],z_box[1],z_box[2],z_box[3]], [z_box[4],z_box[5],z_box[6],z_box[7]], [z_box[0],z_box[1],z_box[5],z_box[4]], [z_box[1],z_box[2],z_box[6],z_box[5]], [z_box[2],z_box[3],z_box[7],z_box[6]], [z_box[3],z_box[0],z_box[4],z_box[7]]]
    ax2.add_collection3d(Poly3DCollection(basis_vlakken, facecolors='gray', alpha=0.05, edgecolors='black', linestyles=':'))

    # Teken alle producten in de lijst (bij 2-zijdig strippen zijn dit er twee)
    for prod in producten_lijst:
        ax2.add_collection3d(Poly3DCollection(prod, facecolors='cyan', alpha=0.8, edgecolors='blue'))

    ax2.set_xlim(0, max(base_L, base_B, base_H)); ax2.set_ylim(0, max(base_L, base_B, base_H)); ax2.set_zlim(0, max(base_L, base_B, base_H))
    ax2.view_init(elev=30, azim=-45); ax2.axis('off')
    st.pyplot(fig2, dpi=80)

# --- DATATABEL ---
st.divider()
st.subheader(f"📋 Maatvoering (Ref: Formulier DEKO)")
data = [
    {"Maat": "A", "Waarde (mm)": A, "Omschrijving": "Lengte eindproduct"},
    {"Maat": "B", "Waarde (mm)": base_B, "Omschrijving": "Breedte basissteen"},
    {"Maat": "C", "Waarde (mm)": C, "Omschrijving": "Hoogte eindproduct"},
    {"Maat": "D", "Waarde (mm)": D, "Omschrijving": "Dikte strip(s)"}
]
st.table(pd.DataFrame(data))
