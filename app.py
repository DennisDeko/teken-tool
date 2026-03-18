import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Transformaties", layout="wide")

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
    
    # Dynamische Variabelen (Formulier Logica A, B, C, D, E, X)
    A = st.number_input("A: Lengte product (mm)", value=base_L)
    B = st.number_input("B: Breedte/Diepte (mm)", value=base_B)
    C = st.number_input("C: Hoogte product (mm)", value=base_H)
    
    # Bepaal Vorm Categorie en activeer specifieke velden
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
    elif type_trans in ["Strippen (1-zijdig)", "Strippen (2-zijdig)", "Kopstrippen", "Kimstenen"]:
        vorm_categorie = "Blok"
        D = st.number_input("D: Strip/Zaag dikte (mm)", value=23.0)
        B = D # Bij een strip wordt de productbreedte gelijk aan D
    elif type_trans == "Afkorten":
        vorm_categorie = "Blok"
        X = st.number_input("X: Afkortmaat (mm)", value=base_L / 2)
        A = X # Bij afkorten is de lengte gelijk aan X

# --- 3D GEOMETRIE ENGINE ---
def genereer_3d_vlakken(profiel_2d, hoogte_c):
    vlakken = []
    n = len(profiel_2d)
    # Bodem en Top (Vlakken)
    vlakken.append([[p[0], p[1], 0] for p in profiel_2d])
    vlakken.append([[p[0], p[1], hoogte_c] for p in profiel_2d])
    # Zijwanden genereren door de punten te verbinden
    for i in range(n):
        p1, p2 = profiel_2d[i], profiel_2d[(i+1)%n]
        vlakken.append([[p1[0], p1[1], 0], [p2[0], p2[1], 0], [p2[0], p2[1], hoogte_c], [p1[0], p1[1], hoogte_c]])
    return vlakken

# 2D Profiel Punten (Bovenaanzicht)
if vorm_categorie == "L-Vorm":
    profiel = [(0,0), (A,0), (A,D), (E,D), (E,B), (0,B)]
elif vorm_categorie == "U-Vorm":
    # Een 'Bak' is een U-vorm: Lange voorzijde en 2 korte koppen
    profiel = [(0,0), (A,0), (A,B), (A-E,B), (A-E,D), (E,D), (E,B), (0,B)]
else: # Blok
    profiel = [(0,0), (A,0), (A,B), (0,B)]

# Genereer 3D Model
product_vlakken = genereer_3d_vlakken(profiel, C)

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"2D Profiel (Top View)")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    
    # Teken originele basissteen ("Restant/Afval" in transparant grijs)
    basis_poly = plt.Polygon([(0,0), (base_L,0), (base_L,base_B), (0,base_B)], facecolor='gray', alpha=0.1, edgecolor='black', linestyle='--')
    ax1.add_patch(basis_poly)

    # Teken het uiteindelijke Product (in Cyaan)
    product_poly = plt.Polygon(profiel, facecolor='cyan', alpha=0.6, edgecolor='blue', linewidth=2)
    ax1.add_patch(product_poly)

    # As limieten
    ax1.set_xlim(-20, base_L + 40)
    ax1.set_ylim(-20, base_B + 40)
    ax1.set_aspect('equal')
    ax1.axis('off')
    st.pyplot(fig1, dpi=80)

with col2:
    st.subheader("3D Product Render")
    fig2 = plt.figure(figsize=(6, 5))
    ax2 = fig2.add_subplot(111, projection='3d')
    
    # Teken Basissteen Spook (Restant)
    z = np.array([[0,0,0], [base_L,0,0], [base_L,base_B,0], [0,base_B,0], [0,0,base_H], [base_L,0,base_H], [base_L,base_B,base_H], [0,base_B,base_H]])
    basis_vlakken = [[z[0],z[1],z[2],z[3]], [z[4],z[5],z[6],z[7]], [z[0],z[1],z[5],z[4]], [z[1],z[2],z[6],z[5]], [z[2],z[3],z[7],z[6]], [z[3],z[0],z[4],z[7]]]
    ax2.add_collection3d(Poly3DCollection(basis_vlakken, facecolors='gray', alpha=0.05, edgecolors='black', linestyles=':'))

    # Teken Product
    ax2.add_collection3d(Poly3DCollection(product_vlakken, facecolors='cyan', alpha=0.8, edgecolors='blue'))

    ax2.set_xlim(0, max(base_L, base_B, base_H))
    ax2.set_ylim(0, max(base_L, base_B, base_H))
    ax2.set_zlim(0, max(base_L, base_B, base_H))
    ax2.view_init(elev=30, azim=-45)
    ax2.axis('off')
    st.pyplot(fig2, dpi=80)

# --- DATATABEL (PDF FORMULIER EXACT) ---
st.divider()
st.subheader(f"📋 Maatvoering (Ref: Formulier DEKO)")

data = [
    {"Maat": "A", "Waarde (mm)": A, "Omschrijving": "Lengte eindproduct"},
    {"Maat": "B", "Waarde (mm)": B, "Omschrijving": "Breedte/Diepte eindproduct"},
    {"Maat": "C", "Waarde (mm)": C, "Omschrijving": "Hoogte eindproduct"}
]

if vorm_categorie in ["L-Vorm", "U-Vorm"] or D > 0:
    data.append({"Maat": "D", "Waarde (mm)": D, "Omschrijving": "Wanddikte 1 (Strek / Voorzijde)"})
if vorm_categorie in ["L-Vorm", "U-Vorm"]:
    data.append({"Maat": "E", "Waarde (mm)": E, "Omschrijving": "Wanddikte 2 (Kop / Zijwanden)"})
if type_trans == "Afkorten":
    data.append({"Maat": "X", "Waarde (mm)": X, "Omschrijving": "Afkortmaat"})

st.table(pd.DataFrame(data))
