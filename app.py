import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

st.title("📏 Mijn 3D Maten Tool")

# Sidebar voor input
st.sidebar.header("Voer de maten in")
l = st.sidebar.slider("Lengte", 1, 100, 10)
b = st.sidebar.slider("Breedte", 1, 100, 5)
h = st.sidebar.slider("Hoogte", 0, 100, 3)

# De teken-functie
fig = plt.figure(figsize=(10, 5))

# 2D Deel
ax1 = fig.add_subplot(121)
rechthoek = plt.Rectangle((0, 0), l, b, fill=None, edgecolor='blue', linewidth=2)
ax1.add_patch(rechthoek)
ax1.set_xlim(-5, l + 5)
ax1.set_ylim(-5, b + 5)
ax1.set_title(f"2D: {l} x {b}")
ax1.set_aspect('equal')

# 3D Deel
if h > 0:
    ax2 = fig.add_subplot(122, projection='3d')
    v = [[0, 0, 0], [l, 0, 0], [l, b, 0], [0, b, 0],
         [0, 0, h], [l, 0, h], [l, b, h], [0, b, h]]
    vlakken = [[v[0], v[1], v[5], v[4]], [v[7], v[6], v[2], v[3]],
                [v[0], v[3], v[7], v[4]], [v[1], v[2], v[6], v[5]],
                [v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]]]
    ax2.add_collection3d(Poly3DCollection(vlakken, facecolors='cyan', linewidths=1, edgecolors='blue', alpha=.25))
    limit = max(l, b, h) + 2
    ax2.set_xlim(0, limit)
    ax2.set_ylim(0, limit)
    ax2.set_zlim(0, limit)
    ax2.set_title(f"3D: {h} hoog")

st.pyplot(fig)
