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
    st.header("1. Projectinformatie")
    project_naam = st.text_input("Project", value="Nieuwbouw Elst")
    sortering = st.text_input("Sortering", value="Rood genuanceerd")
    stuks = st.number_input("Aantal stuks", value=100, step=1)

    st.header("2. Basis Steen")
    keuze_naam = st.selectbox("Kies standaard maat", list(steen_maten.keys()))
    std_l, std_b, std_h = steen_maten[keuze_naam]
    base_L = int(st.number_input("Oorspronkelijke Lengte", value=float(std_l)))
    base_B = int(st.number_input("Oorspronkelijke Breedte", value=float(std_b)))
    base_H = int(st.number_input("Oorspronkelijke Hoogte", value=float(std_h)))
    zaag_dikte = st.slider("Zaagblad dikte (mm)", 0.0, 5.0, 3.0)

    st.header("3. Transformatie & Maten")
    type_trans = st.selectbox("Kies bewerking", transformaties)
    
    A = int(st.number_input("A: Lengte product (mm)", value=float(base_L)))
    C = int(st.number_input("C: Dikte strip (mm)", value=23))
    B_hoogte = int(st.number_input("B: Hoogte product (mm)", value=float(base_H)))

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
    producten_3d.append(genereer_3d_vlakken([(0,0), (A,0), (A,C), (0,C)], B_hoogte))
    if "2-zijdig" in type_trans:
        producten_3d.append(genereer_3d_vlakken([(0, base_B-C), (A, base_B-C), (A, base_B), (0, base_B)], B_hoogte))
else:
    producten_3d.append(genereer_3d_vlakken([(0,0), (A,0), (A,base_B), (0,base_B)], B_hoogte))

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    ax1.add_patch(plt.Rectangle((0,0), base_L, base_B, facecolor='gray', alpha=0.1, edgecolor='black', ls='--'))

    if "Strippen" in type_trans:
        ax1.add_patch(plt.Rectangle((0,0), A, C, facecolor='cyan', alpha=0.6, edgecolor='blue'))
        ax1.annotate('', xy=(A*0.15, 0), xytext=(A*0.15, C), arrowprops=dict(arrowstyle='<->', color='black'))
        ax1.text(A*0.17, C/2, f'C: {C}', fontweight='bold', va='center')
        if "2-zijdig" in type_trans:
            ax1.add_patch(plt.Rectangle((0, base_B-C), A, C, facecolor='cyan', alpha=0.6, edgecolor='blue'))

    ax1.annotate('', xy=(0, -15), xytext=(A, -15), arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(-25, -30, f'A: {A}', ha='left', fontweight='bold') 
    
    ax1.annotate('', xy=(A+35, 0), xytext=(A+35, base_B), arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(A+55, base_B/2, f'B: {B_hoogte}', va='center', fontweight='bold', rotation=270) 

    ax1.set_xlim(-80, base_L + 120); ax1.set_ylim(-60, base_B + 80)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(figsize=(6, 5)); ax2 = fig2.add_subplot(111, projection='3d')
    for prod in producten_3d:
        ax2.add_collection3d(Poly3DCollection(prod, facecolors='cyan', alpha=0.7, edgecolors='blue'))

    ax2.plot([0, A], [-25, -25], [0, 0], color='black', lw=1.5)
    ax2.text(-40, -40, 0, f'A: {A}', fontweight='bold')
    
    ax2.plot([A+25, A+25], [0, 0], [0, B_hoogte], color='black', lw=1.5)
    ax2.text(A+35, 0, B_hoogte/2, f'B: {B_hoogte}', fontweight='bold', va='center')

    ax2.plot([A*0.2, A*0.2], [base_B/2, base_B/2], [B_hoogte + 15, B_hoogte + 40], color='red', lw=2)
    ax2.text(A*0.05, base_B/2, B_hoogte + 45, f'C: {C}', color='red', fontweight='bold', ha='center')

    lim = max(base_L, base_B, B_hoogte + 60)
    ax2.set_xlim(0, lim); ax2.set_ylim(0, lim); ax2.set_zlim(0, lim)
    ax2.view_init(elev=25, azim=-40); ax2.axis('off')
    st.pyplot(fig2)

# --- OVERZICHTSTABEL ---
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📋 Afmetingen")
    st.table(pd.DataFrame([
        {"Maat": "A", "Omschrijving": "Lengte product", "Waarde": f"{A}"},
        {"Maat": "B", "Omschrijving": "Hoogte product", "Waarde": f"{B_hoogte}"},
        {"Maat": "C", "Omschrijving": "Dikte product", "Waarde": f"{C}"}
    ]))

with col_b:
    st.subheader("📄 Projectgegevens")
    st.write(f"**Project:** {project_naam}")
    st.write(f"**Sortering:** {sortering}")
    st.write(f"**Aantal:** {stuks} stuks")
