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

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Projectinformatie")
    project_naam = st.text_input("Project", value="Nieuwbouw Elst")
    sortering = st.text_input("Sortering", value="Rood genuanceerd")
    stuks = st.number_input("Aantal stuks", value=100, step=1)

    st.header("2. Basis Steen")
    keuze_naam = st.selectbox("Kies standaard maat", list(steen_maten.keys()))
    std_l, std_b, std_h = steen_maten[keuze_naam]
    base_L = int(st.number_input("Oorspronkelijke Lengte (A)", value=float(std_l)))
    base_H = int(st.number_input("Oorspronkelijke Hoogte (B)", value=float(std_h)))
    base_B = int(st.number_input("Oorspronkelijke Breedte/Diepte", value=float(std_b)))

    st.header("3. Maten Eindproduct")
    A = int(st.number_input("A: Lengte (mm)", value=base_L))
    B = int(st.number_input("B: Hoogte (mm)", value=base_H))
    C = int(st.number_input("C: Dikte strip (mm)", value=23))

# --- 3D ENGINE ---
def genereer_3d_vlakken(l, b, h, y_offset=0):
    vlakken = [
        [[0, y_offset, 0], [l, y_offset, 0], [l, b+y_offset, 0], [0, b+y_offset, 0]], 
        [[0, y_offset, h], [l, y_offset, h], [l, b+y_offset, h], [0, b+y_offset, h]], 
        [[0, y_offset, 0], [l, y_offset, 0], [l, y_offset, h], [0, y_offset, h]],     
        [[l, y_offset, 0], [l, b+y_offset, 0], [l, b+y_offset, h], [l, y_offset, h]], 
        [[l, b+y_offset, 0], [0, b+y_offset, 0], [0, b+y_offset, h], [l, b+y_offset, h]], 
        [[0, b+y_offset, 0], [0, y_offset, 0], [0, y_offset, h], [0, y_offset, h]]      
    ]
    return vlakken

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    ax1.add_patch(plt.Rectangle((0,0), A, base_B, facecolor='gray', alpha=0.1, edgecolor='black', ls='--'))
    ax1.add_patch(plt.Rectangle((0,0), A, C, facecolor='cyan', alpha=0.6, edgecolor='blue'))
    ax1.add_patch(plt.Rectangle((0, base_B-C), A, C, facecolor='cyan', alpha=0.6, edgecolor='blue'))
    
    # A met dubbele pijl
    ax1.annotate('', xy=(0, -10), xytext=(A, -10), arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(A/2, -25, f"A: {A}", ha='center', fontweight='bold')
    
    # B met dubbele pijl
    ax1.annotate('', xy=(A+15, 0), xytext=(A+15, base_B), arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(A+30, base_B/2, f"B: {B}", va='center', fontweight='bold', rotation=270)
    
    # C met dubbele pijl
    ax1.annotate('', xy=(A*0.1, 0), xytext=(A*0.1, C), arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text(A*0.15, C/2, f"C: {C}", va='center', fontweight='bold')

    ax1.set_xlim(-40, A+60); ax1.set_ylim(-40, base_B+30); ax1.axis('off')
    st.pyplot(fig1)

with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(figsize=(6, 5)); ax2 = fig2.add_subplot(111, projection='3d')
    
    # Strippen tekenen
    ax2.add_collection3d(Poly3DCollection(genereer_3d_vlakken(A, C, B, 0), facecolors='cyan', alpha=0.7, edgecolors='blue'))
    ax2.add_collection3d(Poly3DCollection(genereer_3d_vlakken(A, C, B, base_B-C), facecolors='cyan', alpha=0.7, edgecolors='blue'))

    # MAAT A - Dubbele pijl op de voorgrond
    ax2.annotate('', xy=(0, -30), xytext=(A, -30), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5), annotation_clip=False)
    ax2.text(A/2, -50, 0, f"A: {A}", ha='center', fontweight='bold', zorder=10)

    # MAAT B - Verticale dubbele pijl op de voorgrond
    ax2.plot([A+20, A+20], [-10, -10], [0, B], color='black', lw=1.5, marker='v', markevery=[0, -1])
    ax2.text(A+35, -10, B/2, f"B: {B}", fontweight='bold', va='center', zorder=10)

    # MAAT C - Rode dubbele pijl voor dikte op de voorgrond
    ax2.plot([-15, -15], [0, C], [B/2, B/2], color='red', lw=2, marker='|', markevery=[0, -1])
    ax2.text(-65, 0, B/2, f"C: {C}", color='red', fontweight='bold', zorder=10)

    ax2.set_xlim(0, A); ax2.set_ylim(-40, base_B); ax2.set_zlim(0, B+20)
    ax2.view_init(elev=20, azim=-35); ax2.axis('off')
    st.pyplot(fig2)

# --- OVERZICHT ---
st.divider()
st.subheader("📋 Projectoverzicht")
c1, c2 = st.columns(2)
with c1:
    st.write(f"**Project:** {project_naam}")
    st.write(f"**Sortering:** {sortering}")
    st.write(f"**Aantal:** {stuks} stuks")
with c2:
    st.table(pd.DataFrame([{"Maat A (Lengte)": A, "Maat B (Hoogte)": B, "Maat C (Dikte)": C}]))
