import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

st.set_page_config(page_title="Maten Tool", layout="wide")
st.title("📏 Exacte Maten Visualisatie")

# Sidebar voor vrije invoer
st.sidebar.header("Voer je maten in")
l = st.sidebar.number_input("Lengte", min_value=0.1, value=100.0, step=0.1)
b = st.sidebar.number_input("Breedte", min_value=0.1, value=50.0, step=0.1)
h = st.sidebar.number_input("Hoogte (0 voor 2D)", min_value=0.0, value=20.0, step=0.1)

# Layout: twee kolommen voor de tekeningen
col1, col2 = st.columns(2)

fig1, ax1 = plt.subplots()
rechthoek = plt.Rectangle((0, 0), l, b, fill=None, edgecolor='blue', linewidth=2)
ax1.add_patch(rechthoek)
margin = max(l, b) * 0.1
ax1.set_xlim(-margin, l + margin)
ax1.set_ylim(-margin, b + margin)
ax1.set_title(f"Bovenaanzicht: {l} x {b}")
ax1.set_aspect('equal')
col1.pyplot(fig1)

if h > 0:
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    
    # Hoekpunten
    v = [[0, 0, 0], [l, 0, 0], [l, b, 0], [0, b, 0],
         [0, 0, h], [l, 0, h], [l, b, h], [0, b, h]]
    
    # Vlakken
    vlakken = [[v[0], v[1], v[5], v[4]], [v[7], v[6], v[2], v[3]],
                [v[0], v[3], v[7], v[4]], [v[1], v[2], v[6], v[5]],
                [v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]]]
    
    ax2.add_collection3d(Poly3DCollection(vlakken, facecolors='cyan', linewidths=1, edgecolors='blue', alpha=.25))
    
    # Zorg dat de assen gelijkmatig schalen
    max_dim = max(l, b, h)
    ax2.set_xlim(0, max_dim)
    ax2.set_ylim(0, max_dim)
    ax2.set_zlim(0, max_dim)
    ax2.set_title(f"3D Model: {h} hoog")
    col2.pyplot(fig2)
else:
    col2.write("Voer een hoogte in voor de 3D weergave.")
