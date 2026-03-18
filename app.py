import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

# --- CONFIGURATIE ---
st.set_page_config(page_title="DEKO Product Generator", layout="wide")

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
    
    A = st.number_input("A: Lengte product (mm)", value=base_L)
    B = st.number_input("B: Breedte/Diepte totaal (mm)", value=base_B)
    C = st.number_input("C: Dikte product (mm)", value=23.0)

# --- 3D ENGINE ---
def genereer_3d_vlakken(profiel_2d, hoogte, z_offset=0):
    vlakken = []
    vlakken.append([[p[0], p[1], z_offset] for p in profiel_2d])
    vlakken.append([[p[0], p[1], hoogte + z_offset] for p in profiel_2d])
    for i in range(len(profiel_2d)):
        p1, p2 = profiel_2d[i], profiel_2d[(i+1)%len(profiel_2d)]
        vlakken.append([[p1[0], p1[1], z_offset], [p2[0], p2[1], z_offset], 
                        [p2[0], p2[1], hoogte + z_offset], [p1[0], p1[1], hoogte + z_offset]])
    return vlakken

producten_3d = []
if "Strippen" in type_trans:
    producten_3d.append(genereer_3d_vlakken([(0,0), (A,0), (A,C), (0,C)], base_H))
    if "2-zijdig" in type_trans:
        producten_3d.append(genereer_3d_vlakken([(0, B-C), (A, B-C), (A, B), (0, B)], base_H))
else:
    producten_3d.append(genereer_3d_vlakken([(0,0), (A,0), (A,B), (0,B)], base_H))

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    ax1.add_patch(plt.Rectangle((0,0), base_L, base_B, facecolor='gray', alpha=0.1, edgecolor='black', ls='--'))

    if "Strippen" in type_trans:
        ax1.add_patch(plt.Rectangle((0,0), A, C, facecolor='cyan', alpha=0.6, edgecolor='blue'))
        ax1.annotate('', xy=(A*0.15, 0), xytext=(A*0.15, C), arrowprops=dict(arrowstyle='<->', color='black'))
        ax1.text(A*0.17, C/2, f'C: {C}mm', fontweight='bold', va='center')
        if "2-zijdig" in type_trans:
            ax1.add_patch(plt.Rectangle((0, B-C), A, C, facecolor='cyan', alpha=0.6, edgecolor='blue'))

    # Maten in 2D (A naar links, B verder naar rechts)
    ax1.annotate('', xy=(0, -15), xytext=(A, -15), arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(-10, -30, f'A: {A}mm', ha='left', fontweight='bold') 
    
    ax1.annotate('', xy=(A+35, 0), xytext=(A+35, B), arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(A+55, B/2, f'B: {B}mm', va='center', fontweight='bold', rotation=270) 

    ax1.set_xlim(-70, base_L + 120); ax1.set_ylim(-70, base_B + 100)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(figsize=(6, 5)); ax2 = fig2.add_subplot(111, projection='3d')
    for prod in producten_3d:
        ax2.add_collection3d(Poly3DCollection(prod, facecolors='cyan', alpha=0.7, edgecolors='blue'))

    # Maten in 3D
    # A (Lengte)
    ax2.plot([0, A], [-20, -20], [0, 0], color='black', lw=1.5)
    ax2.text(A/2, -35, 0, f'A: {A}mm', fontweight='bold', ha='center')
    
    # B (Breedte)
    ax2.plot([A+20, A+20], [0, B], [0, 0], color='black', lw=1.5)
    ax2.text(A+35, B/2, 0, f'B: {B}mm', fontweight='bold', va='center')

    # C (Dikte) Zwevend boven de tekening
    ax2.plot([A/2, A/2], [B/2, B/2], [base_H + 5, base_H + 25], color='red', lw=2)
    ax2.text(A/2, B/2, base_H + 30, f'C: {C}mm', color='red', fontweight='bold', ha='center')

    # Bereik instellen voor goede weergave labels
    lim = max(base_L, base_B, base_H + 40)
    ax2.set_xlim(0, lim); ax2.set_ylim(0, lim); ax2.set_zlim(0, lim)
    ax2.view_init(elev=25, azim=-40); ax2.axis('off')
    st.pyplot(fig2)

# --- TABEL ---
st.divider()
st.table(pd.DataFrame([
    {"Maat": "A", "Omschrijving": "Lengte product", "Waarde": f"{A} mm"},
    {"Maat": "B", "Omschrijving": "Breedte totaal", "Waarde": f"{B} mm"},
    {"Maat": "C", "Omschrijving": "Dikte product", "Waarde": f"{C} mm"}
]))
