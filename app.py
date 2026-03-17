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
    st.title("Universele Maten Tool Pro (mm)")

st.divider()

# --- INPUT SECTIE ---
vorm_type = st.sidebar.selectbox("Kies een vorm", ["Rechthoek / Balk", "L-Vorm"])

st.sidebar.subheader("Zaagsnede Instellingen")
aantal_x = st.sidebar.slider("Aantal Zaagsnedes X (Verticaal)", 0, 10, 0)
aantal_y = st.sidebar.slider("Aantal Zaagsnedes Y (Horizontaal)", 0, 10, 0)

posities_x = []
for i in range(aantal_x):
    pos = st.sidebar.number_input(f"Positie X-{i+1} (mm)", value=100.0 + (i*100.0), key=f"x_{i}")
    posities_x.append(pos)

posities_y = []
for i in range(aantal_y):
    pos = st.sidebar.number_input(f"Positie Y-{i+1} (mm)", value=100.0 + (i*100.0), key=f"y_{i}")
    posities_y.append(pos)

st.sidebar.divider()

if vorm_type == "Rechthoek / Balk":
    l1 = st.sidebar.number_input("Lengte (mm)", min_value=1.0, value=1000.0)
    l2 = st.sidebar.number_input("Breedte (mm)", min_value=1.0, value=500.0)
    h = st.sidebar.number_input("Hoogte (mm)", min_value=0.1, value=400.0)
    dikte = 0.0
    grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
else:
    l1 = st.sidebar.number_input("Lengte Zijde 1 (mm)", min_value=1.0, value=1000.0)
    l2 = st.sidebar.number_input("Lengte Zijde 2 (mm)", min_value=1.0, value=600.0)
    limiet = float(min(l1, l2))
    dikte = st.sidebar.number_input("Dikte (mm)", min_value=0.1, max_value=limiet, value=200.0)
    h = st.sidebar.number_input("Hoogte (mm)", min_value=0.1, value=300.0)
    grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
    vlak_indices = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]]

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Bovenaanzicht (mm)")
    fig1, ax1 = plt.subplots()
    omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='blue', linewidth=2)
    ax1.add_patch(omtrek)
    
    for i, px in enumerate(posities_x):
        y_lim = l2 if (vorm_type == "Rechthoek / Balk" or px <= dikte) else dikte
        ax1.plot([px, px], [0, y_lim], color='red', linestyle='--', linewidth=1.5)
        ax1.text(px, y_lim + (max(l1,l2)*0.03), f"X{i+1}:{int(px)}", color='red', fontsize=9, ha='center', weight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
            
    for i, py in enumerate(posities_y):
        x_lim = l1 if (vorm_type == "Rechthoek / Balk" or py <= dikte) else dikte
        ax1.plot([0, x_lim], [py, py], color='red', linestyle='--', linewidth=1.5)
        ax1.text(x_lim + (max(l1,l2)*0.03), py, f"Y{i+1}:{int(py)}", color='red', fontsize=9, va='center', weight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    m = max(l1, l2) * 1.2
    ax1.set_xlim(-50, m); ax1.set_ylim(-50, m); ax1.set_aspect('equal'); ax1.grid(True, linestyle=':', alpha=0.3)
    st.pyplot(fig1)

with col2:
    st.subheader("3D Model (mm)")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    
    v_3d = []
    for p in grond_poly: v_3d.append([p[0], p[1], 0])
    for p in grond_poly: v_3d.append([p[0], p[1], h])
    v_3d = np.array(v_3d)
    vlakken = [[v_3d[i] for i in idx] for idx in vlak_indices]
    
    k = 'cyan' if vorm_type == "Rechthoek / Balk" else 'orange'
    poly3d = Poly3DCollection(vlakken, facecolors=k, linewidths=1, edgecolors='blue', alpha=.15)
    ax2.add_collection3d(poly3d)
    
    # Zaagsnedes in 3D (Hoger geplaatste labels met achtergrond)
    # De tekst staat nu op Hoogte + 15% van de totale hoogte
    label_h_offset = h + (max(l1, l2, h) * 0.15)

    for i, px in enumerate(posities_x):
        y_top = l2 if (vorm_type == "Rechthoek / Balk" or px <= dikte) else dikte
        zs_vlak = np.array([[px, 0, 0], [px, y_top, 0], [px, y_top, h], [px, 0, h]])
        ax2.add_collection3d(Poly3DCollection([zs_vlak], facecolors='red', alpha=0.9, edgecolors='darkred', linewidths=2))
        ax2.text(px, y_top/2, label_h_offset, f"X{i+1}:{int(px)}", color='red', weight='bold', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))

    for i, py in enumerate(posities_y):
        x_top = l1 if (vorm_type == "Rechthoek / Balk" or py <= dikte) else dikte
        zs_vlak = np.array([[0, py, 0], [x_top, py, 0], [x_top, py, h], [0, py, h]])
        ax2.add_collection3d(Poly3DCollection([zs_vlak], facecolors='red', alpha=0.9, edgecolors='darkred', linewidths=2))
        ax2.text(x_top/2, py, label_h_offset, f"Y{i+1}:{int(py)}", color='red', weight='bold', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))

    d = max(l1, l2, h)
    ax2.set_xlim(0, d); ax2.set_ylim(0, d); ax2.set_zlim(0, d)
    
    # Schone achtergrond
    ax2.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax2.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax2.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax2.grid(False)
    
    ax2.set_xlabel('X (mm)'); ax2.set_ylabel('Y (mm)'); ax2.set_zlabel('H (mm)')
    st.pyplot(fig2)

# --- OVERZICHT ---
st.divider()
st.subheader("📋 Overzicht (mm)")
overzicht_data = {"Item": ["Lengte", "Breedte", "Hoogte", "Dikte"], "Waarde": [f"{int(l1)}", f"{int(l2)}", f"{int(h)}", f"{int(dikte) if dikte > 0 else 'N.v.t.'}"]}
for i, px in enumerate(posities_x):
    overzicht_data["Item"].append(f"Zaagsnede X-{i+1}"); overzicht_data["Waarde"].append(f"{int(px)}")
for i, py in enumerate(posities_y):
    overzicht_data["Item"].append(f"Zaagsnede Y-{i+1}"); overzicht_data["Waarde"].append(f"{int(py)}")

st.table(pd.DataFrame(overzicht_data))
