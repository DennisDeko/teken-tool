import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

st.set_page_config(page_title="Maten Tool Pro", layout="wide")
st.title("📏 Universele Maten Tool")

# 1. Kies het type vorm
vorm_type = st.sidebar.selectbox("Kies een vorm", ["Rechthoek / Balk", "L-Vorm"])

st.sidebar.divider()

# 2. Input op basis van keuze
if vorm_type == "Rechthoek / Balk":
    l1 = st.sidebar.number_input("Lengte (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Breedte (cm)", min_value=1.0, value=50.0)
    h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=40.0)
    # Punten voor rechthoek
    grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    vlak_indices = [
        [0, 1, 2, 3], # Bodem
        [4, 5, 6, 7], # Deksel
        [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7] # Zijwanden
    ]
else:
    l1 = st.sidebar.number_input("Lengte Zijde 1 (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Lengte Zijde 2 (cm)", min_value=1.0, value=60.0)
    dikte = st.sidebar.number_input("Dikte (cm)", min_value=0.1, max_value=float(min(l1, l2)), value=20.0)
    h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=30.0)
    # Punten voor L-vorm
    grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
    vlak_indices = [
        [0, 1, 2, 3, 4, 5], # Bodem
        [6, 7, 8, 9, 10, 11], # Deksel
        [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]
    ]

# --- Visualisatie (2D & 3D) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"2D Bovenaanzicht ({vorm_type})")
    fig1, ax1 = plt.subplots()
    omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='blue', linewidth=2)
    ax1.add_patch(omtrek)
    
    # Gebruik de maximale maat voor een mooie schaal
    max_l = max(l1, l2)
    ax1.set_xlim(-5, max_l + 5)
    ax1.set_ylim(-5, max_
