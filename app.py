import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

st.set_page_config(page_title="L-Vorm Tool", layout="wide")
st.title("📐 L-Vorm: 2D Tekening & 3D Model")

# Sidebar
st.sidebar.header("Afmetingen")
l1 = st.sidebar.number_input("Lengte Zijde 1 (cm)", min_value=1.0, value=100.0)
l2 = st.sidebar.number_input("Lengte Zijde 2 (cm)", min_value=1.0, value=60.0)
dikte = st.sidebar.number_input("Materiaaldikte (cm)", min_value=0.1, max_value=float(min(l1, l2)), value=20.0)
h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=30.0)

# Punten voor de L-vorm (Bovenaanzicht)
p0 = [0, 0]
p1 = [l1, 0]
p2 = [l1, dikte]
p3 = [dikte, dikte]
p4 = [dikte, l2]
p5 = [0, l2]
grond_poly = np.array([p0, p1, p2, p3, p4, p5])

# Layout: Twee kolommen
col1, col2 = st.columns(2)

# --- Kolom 1: 2D Bovenaanzicht ---
with col1:
    st.subheader("Bovenaanzicht (2D)")
    fig1, ax1 = plt.subplots()
    # Teken de omtrek van de L
    omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='blue', linewidth=2)
    ax1.add_patch(omtrek)
    
    # Automatisch zoomen
    ax1.set_xlim(-5, l1 + 5)
    ax1.set_ylim(-5, l2 + 5)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6) # Hulplijntjes voor 2D zijn vaak wel fijn
    st.pyplot(fig1)

# --- Kolom 2: 3D Model ---
with col2:
    st.subheader("Ruimtelijk Model (3D)")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    
    # 3D Punten maken
    v = []
    for p in grond_poly:
        v.append([p[0], p[1], 0]) # Onderkant
    for p in grond_poly:
        v.append([p[0], p[1], h]) # Bovenkant
    v = np.array(v)

    # Vlakken voor de 3D L-vorm
    vlakken = [
        [v[0], v[1], v[2], v[3], v[4], v[5]], # Bodem
        [v[6], v[7], v[8], v[9], v[10], v[11]], # Deksel
        [v[0], v[1], v[7], v[6]], # Zijwand buiten 1
        [v[1], v[2], v[8], v[7]], # Kopse kant 1
        [v[2], v[3], v[9], v[8]], # Zijwand binnen 1
        [v[3], v[4], v[10], v[9]], # Zijwand binnen 2
        [v[4], v[5], v[11], v[10]], # Kopse kant 2
        [v[5], v[0], v[6], v[11]]  # Zijwand buiten 2
    ]
    
    poly3d = Poly3DCollection(vlakken, facecolors='orange', linewidths=1, edgecolors='brown', alpha=.4)
    ax2.add_collection3d(poly3d)

    # Assen instellen
    max_dim = max(l1, l2, h)
    ax2.set_xlim(0, max_dim)
    ax2.set_ylim(0, max_dim)
    ax2.set_zlim(0, max_dim)
    
    # Schone achtergrond (geen blokjes)
    ax2.grid(False)
    ax2.xaxis.pane.fill = ax2.yaxis.pane.fill = ax2.zaxis.pane.fill = False
    
    st.pyplot(fig2)

st.divider()
st.write(f"**Check:** Zijde 1 is {l1}cm, Zijde 2 is {l2}cm met een dikte van {dikte}cm.")
