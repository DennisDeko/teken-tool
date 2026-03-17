import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"

col_logo, col_titel = st.columns([1, 3])
with col_logo:
    st.image(LOGO_URL, use_container_width=True)
with col_titel:
    st.title("Universele Maten Tool Pro")

st.divider()

# --- INPUT SECTIE ---
vorm_type = st.sidebar.selectbox("Kies een vorm", ["Rechthoek / Balk", "L-Vorm"])

# ZAAGSNEDE INSTELLINGEN (DYNAMISCH)
st.sidebar.subheader("Zaagsnede Instellingen")
aantal_x = st.sidebar.slider("Aantal Zaagsnedes X (Verticaal)", 0, 5, 0)
aantal_y = st.sidebar.slider("Aantal Zaagsnedes Y (Horizontaal)", 0, 5, 0)

posities_x = []
for i in range(aantal_x):
    pos = st.sidebar.number_input(f"Positie X-{i+1} (cm)", value=10.0 + (i*10.0), key=f"x_{i}")
    posities_x.append(pos)

posities_y = []
for i in range(aantal_y):
    pos = st.sidebar.number_input(f"Positie Y-{i+1} (cm)", value=10.0 + (i*10.0), key=f"y_{i}")
    posities_y.append(pos)

st.sidebar.divider()

# MATEN VAN DE VORM
if vorm_type == "Rechthoek / Balk":
    l1 = st.sidebar.number_input("Lengte (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Breedte (cm)", min_value=1.0, value=50.0)
    h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=40.0)
    dikte = 0.0
    grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
else:
    l1 = st.sidebar.number_input("Lengte Zijde 1 (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Lengte Zijde 2 (cm)", min_value=1.0, value=60.0)
    limiet = float(min(l1, l2))
    dikte = st.sidebar.number_input("Dikte (cm)", min_value=0.1, max_value=limiet, value=20.0)
    h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=30.0)
    grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
    vlak_indices = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]]

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Bovenaanzicht")
    fig1, ax1 = plt.subplots()
    omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='blue', linewidth=2)
    ax1.add_patch(omtrek)
    
    for px in posities_x:
        if vorm_type == "Rechthoek / Balk":
            ax1.axvline(x=px, color='red', linestyle='--', linewidth=1.2)
        else:
            y_max = l2 if px <= dikte else dikte
            ax1.plot([px, px], [0, y_max], color='red', linestyle='--', linewidth=1.2)
            
    for py in posities_y:
        if vorm_type == "Rechthoek / Balk":
            ax1.axhline(y=py, color='red', linestyle='--', linewidth=1.2)
        else:
            x_max = l1 if py <= dikte else dikte
            ax1.plot([0, x_max], [py, py], color='red', linestyle='--', linewidth=1.2)
    
    m = max(l1, l2) + 5
    ax1.set_xlim(-5, m); ax1.set_ylim(-5, m); ax1.set_aspect('equal'); ax1.grid(True, linestyle=':', alpha=0.3)
    st.pyplot(fig1)

with col2:
    st.subheader("3D Model")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    v_3d = []
    for p in grond_poly: v_3d.append([p[0], p[1], 0])
    for p in grond_poly: v_3d.append([p[0], p[1], h])
    v_3d = np.array(v_3d)
    vlakken = [[v_3d[i] for i in idx] for idx in vlak_indices]
    k = 'cyan' if vorm_type == "Rechthoek / Balk" else 'orange'
    poly3d = Poly3DCollection(vlakken, facecolors=k, linewidths=1, edgecolors='blue', alpha=.4)
    ax2.add_collection3d(poly3d)
    d = max(l1, l2, h)
    ax2.set_xlim(0, d); ax2.set_ylim(0, d); ax2.set_zlim(0, d)
    ax2.grid(False); ax2.xaxis.pane.fill = ax2.yaxis.pane.fill = ax2.zaxis.pane.fill = False
    st.pyplot(fig2)

# --- OVERZICHT ---
st.divider()
st.subheader("📋 Overzicht Maten")

# De kolommen heten nu simpelweg 'Item' en 'Maat' om fouten te voorkomen
overzicht_data = {
    "Item": ["Lengte (cm)", "Breedte (cm)", "Hoogte (cm)", "Dikte (cm)"],
    "Waarde": [f"{l1}", f"{l2}", f"{h}", f"{dikte}" if dikte > 0 else "N.v.t."]
}

# We voegen de zaagsnedes toe
for i, px in enumerate(posities_x):
    overzicht_data["Item"].append(f"Zaagsnede X-{i+1} (cm)")
    overzicht_data["Waarde"].append(f"{px}")

for i, py in enumerate(posities_y):
    overzicht_data["Item"].append(f"Zaagsnede Y-{i+1} (cm)")
    overzicht_data["Waarde"].append(f"{py}")

# Tabel tonen
st.table(pd.DataFrame(overzicht_data))
