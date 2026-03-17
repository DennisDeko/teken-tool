import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

st.set_page_config(page_title="Maten Tool Pro", layout="wide")
st.title("📐 3D Visualisatie met Schuine Hoeken")

# Sidebar
st.sidebar.header("Basis Maten")
l = st.sidebar.number_input("Lengte (onder)", min_value=0.1, value=100.0)
b = st.sidebar.number_input("Breedte (onder)", min_value=0.1, value=50.0)
h = st.sidebar.number_input("Hoogte", min_value=0.0, value=40.0)

st.sidebar.header("Hoek Instellingen (Offset)")
off_x = st.sidebar.number_input("Verschuiving X (bovenkant)", value=20.0)
off_y = st.sidebar.number_input("Verschuiving Y (bovenkant)", value=0.0)

# Berekening punten
# Onderkant (0 hoogte)
p0 = [0, 0, 0]
p1 = [l, 0, 0]
p2 = [l, b, 0]
p3 = [0, b, 0]

# Bovenkant (met offset)
p4 = [off_x, off_y, h]
p5 = [l + off_x, off_y, h]
p6 = [l + off_x, b + off_y, h]
p7 = [off_x, b + off_y, h]

v = np.array([p0, p1, p2, p3, p4, p5, p6, p7])

# Vlakken definieren
vlakken = [
    [v[0], v[1], v[2], v[3]], # Onder
    [v[4], v[5], v[6], v[7]], # Boven
    [v[0], v[1], v[5], v[4]], # Voor
    [v[2], v[3], v[7], v[6]], # Achter
    [v[1], v[2], v[6], v[5]], # Rechts
    [v[0], v[3], v[7], v[4]]  # Links
]

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Teken de vorm
poly = Poly3DCollection(vlakken, facecolors='cyan', linewidths=1, edgecolors='blue', alpha=.20)
ax.add_collection3d(poly)

# Schaling en assen
all_points = v
max_val = np.max(all_points)
min_val = np.min(all_points)

ax.set_xlim(min_val, max_val)
ax.set_ylim(min_val, max_val)
ax.set_zlim(0, max_val)

# Grid verwijderen
ax.grid(False)
ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False

st.pyplot(fig)

# Bereken de hoek in graden voor de gebruiker
if h > 0:
    hoek_x = np.degrees(np.arctan(off_x / h))
    st.info(f"De hoek van de zijwand t.o.v. verticaal is ongeveer **{abs(hoek_x):.1f}°**")
