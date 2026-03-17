import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

st.set_page_config(page_title="L-Vorm Tool", layout="wide")
st.title("📐 3D L-Vorm Visualisatie")

# Sidebar
st.sidebar.header("Afmetingen L-Vorm")
l1 = st.sidebar.number_input("Lengte Zijde 1 (cm)", min_value=1.0, value=100.0)
l2 = st.sidebar.number_input("Lengte Zijde 2 (cm)", min_value=1.0, value=60.0)
dikte = st.sidebar.number_input("Materiaaldikte (cm)", min_value=0.1, value=20.0)
h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=30.0)

# Definieer de 6 grondpunten van de L-vorm
# We tekenen de L in het X-Y vlak
p0 = [0, 0, 0]
p1 = [l1, 0, 0]
p2 = [l1, dikte, 0]
p3 = [dikte, dikte, 0]
p4 = [dikte, l2, 0]
p5 = [0, l2, 0]

grondpunten = [p0, p1, p2, p3, p4, p5]

# Maak de 3D punten (onderkant en bovenkant)
v = []
for p in grondpunten:
    v.append(p) # Onderkant (z=0)
for p in grondpunten:
    v.append([p[0], p[1], h]) # Bovenkant (z=h)

v = np.array(v)

# Definieer de vlakken (6 zijwanden + onderkant + bovenkant)
vlakken = [
    [v[0], v[1], v[2], v[3], v[4], v[5]], # Bodem
    [v[6], v[7], v[8], v[9], v[10], v[11]], # Deksel
    [v[0], v[1], v[7], v[6]], # Buitenkant lang
    [v[1], v[2], v[8], v[7]], # Kopse kant 1
    [v[2], v[3], v[9], v[8]], # Binnenhoek 1
    [v[3], v[4], v[10], v[9]], # Binnenhoek 2
    [v[4], v[5], v[11], v[10]], # Kopse kant 2
    [v[5], v[0], v[6], v[11]]  # Buitenkant kort
]

# Tekenen
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

poly = Poly3DCollection(vlakken, facecolors='orange', linewidths=1, edgecolors='brown', alpha=.5)
ax.add_collection3d(poly)

# Schaling instellen
max_dim = max(l1, l2, h)
ax.set_xlim(0, max_dim)
ax.set_ylim(0, max_dim)
ax.set_zlim(0, max_dim)

# Grid uit
ax.grid(False)
ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
ax.set_xlabel('Lengte 1')
ax.set_ylabel('Lengte 2')

st.pyplot(fig)

st.info(f"Dit object heeft een totaal grondoppervlak van: **{(l1 * dikte) + ((l2 - dikte) * dikte):.1f} cm²**")
