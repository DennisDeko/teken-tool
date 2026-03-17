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

# --- SIDEBAR INSTELLINGEN ---
vorm_type = st.sidebar.selectbox("Kies type", ["Steen", "Hoek"])
st.sidebar.divider()

# 1. Maat Steen (Uitklapbaar)
with st.sidebar.expander("Maat Steen", expanded=True):
    if vorm_type == "Steen":
        # Gebruik Markdown voor gekleurde labels in de sidebar
        st.write("🟢 **Zijde L1**")
        l1 = st.number_input("Lengte (mm)", min_value=1.0, value=210.0, key="l1_s")
        
        st.write("🔵 **Zijde L2**")
        l2 = st.number_input("Breedte (mm)", min_value=1.0, value=100.0, key="l2_s")
        
        st.write("⚪ **Hoogte H**")
        h = st.number_input("Hoogte (mm)", min_value=0.1, value=50.0, key="h_s")
        
        dikte = 0.0
        grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        
        labels_2d = [
            {'pos': [l1/2, -15], 'text': f'L1: {int(l1)}', 'color': 'green'},
            {'pos': [l1 + 15, l2/2], 'text': f'L2: {int(l2)}', 'color': 'blue', 'rotation': 90}
        ]
    else:
        st.write("🟢 **Zijde L1**")
        l1 = st.number_input("Lengte L1 (mm)", min_value=1.0, value=210.0, key="l1_h")
        
        st.write("🔵 **Zijde L2**")
        l2 = st.number_input("Lengte L2 (mm)", min_value=1.0, value=100.0, key="l2_h")
        
        limiet = float(min(l1, l2))
        st.write("🟠 **Dikte D**")
        dikte = st.number_input("Dikte (mm)", min_value=0.1, max_value=limiet, value=23.0, key="d_h")
        
        st.write("⚪ **Hoogte H**")
        h = st.number_input("Hoogte (mm)", min_value=0.1, value=50.0, key="h_h")
        
        grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]]
        
        labels_2d = [
            {'pos': [l1/2, -15], 'text': f'L1: {int(l1)}', 'color': 'green'},
            {'pos': [-15, l2/2], 'text': f'L2: {int(l2)}', 'color': 'blue', 'rotation': 90},
            {'pos': [dikte/2, dikte + 10], 'text': f'D: {int(dikte)}', 'color': 'orange'}
        ]

# 2. Zaagsnede (Uitklapbaar)
with st.sidebar.expander("Zaagsnede Instellingen", expanded=False):
    st.write("🔴 **Verticale sneden**")
    aantal_x = st.slider("Aantal Zaagsnedes X", 0, 10, 0)
    posities_x = []
    for i in range(aantal_x):
        pos = st.number_input(f"Positie X-{i+1} (mm)", value=50.0 + (i*50.0), key=f"x_{i}")
        posities_x.append(pos)

    st.divider()
    
    st.write("🔴 **Horizontale sneden**")
    aantal_y = st.slider("Aantal Zaagsnedes Y", 0, 10, 0)
    posities_y = []
    for i in range(aantal_y):
        pos = st.number_input(f"Positie Y-{i+1} (mm)", value=25.0 + (i*25.0), key=f"y_{i}")
        posities_y.append(pos)

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"2D Bovenaanzicht {vorm_type}")
    fig1, ax1 = plt.subplots()
    
    # Teken de omtrek
    omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='black', linewidth=1, alpha=0.3)
    ax1.add_patch(omtrek)
    
    # Kleurmarkering zijden (overeenkomstig met sidebar)
    if vorm_type == "Steen":
        ax1.plot([0, l1], [0, 0], color='green', linewidth=4) # L1 onder
        ax1.plot([l1, l1], [0, l2], color='blue', linewidth=4)  # L2 rechts
    else:
        ax1.plot([0, l1], [0, 0], color='green', linewidth=4) # L1
        ax1.plot([0, 0], [0, l2], color='blue', linewidth=4)  # L2
        ax1.plot([0, dikte], [dikte, dikte], color='orange', linewidth=3, linestyle=':') # Dikte

    # Labels toevoegen
    for lbl in labels_2d:
        ax1.text(lbl['pos'][0], lbl['pos'][1], lbl['text'], 
                 color=lbl['color'], weight='bold', fontsize=10,
                 ha='center', va='center', rotation=lbl.get('rotation', 0))

    # Zaagsnedes
    for i, px in enumerate(posities_x):
        y_lim = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        ax1.plot([px, px], [0, y_lim], color='red', linestyle='--', linewidth=1.5)
        ax1.text(px, y_lim + (max(l1,l2)*0.05), f"X{i+1}:{int(px)}", color='red', fontsize=9, ha='center', weight='bold')
            
    for i, py in enumerate(posities_y):
        x_lim = l1 if (vorm_type == "Steen" or py <= dikte) else dikte
        ax1.plot([0, x_lim], [py, py], color='red', linestyle='--', linewidth=1.5)
        ax1.text(x_lim + (max(l1,l2)*0.05), py, f"Y{i+1}:{int(py)}", color='red', fontsize=9, va='center', weight='bold')
    
    m = max(l1, l2) * 1.3
    ax1.set_xlim(-50, m); ax1.set_ylim(-50, m); ax1.set_aspect('equal')
    st.pyplot(fig1)

with col2:
    st.subheader(f"3D Model {vorm_type}")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    
    v_3d = []
    for p in grond_poly: v_3d.append([p[0], p[1], 0])
    for p in grond_poly: v_3d.append([p[0], p[1], h])
    v_3d = np.array(v_3d)
    vlakken = [[v_3d[i] for i in idx] for idx in vlak_indices]
    
    k = 'cyan' if vorm_type == "Steen" else 'orange'
    poly3d = Poly3DCollection(vlakken, facecolors=k, linewidths=1, edgecolors='blue', alpha=.15)
    ax2.add_collection3d(poly3d)
    
    label_h_offset = h + (max(l1, l2, h) * 0.2)

    for i, px in enumerate(posities_x):
        y_top = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        zs_vlak = np.array([[px, 0, 0], [px, y_top, 0], [px, y_top, h], [px, 0, h]])
        ax2.add_collection3d(Poly3DCollection([zs_vlak], facecolors='red', alpha=0.8, edgecolors='darkred'))
        ax2.text(px, y_top/2, label_h_offset, f"X{i+1}:{int(px)}", color='red', weight='bold', fontsize=9)

    for i, py in enumerate(posities_y):
        x_top = l1 if (vorm_type == "Steen" or py <= dikte) else dikte
        zs_vlak = np.array([[0, py, 0], [x_top, py, 0], [x_top, py, h], [0, py, h]])
        ax2.add_collection3d(Poly3DCollection([zs_vlak], facecolors='red', alpha=0.8, edgecolors='darkred'))
        ax2.text(x_top/2, py, label_h_offset, f"Y{i+1}:{int(py)}", color='red', weight='bold', fontsize=9)

    d = max(l1, l2, h)
    ax2.set_xlim(0, d); ax2.set_ylim(0, d); ax2.set_zlim(0, d)
    ax2.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax2.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax2.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax2.grid(False)
    st.pyplot(fig2)

# --- OVERZICHT ---
st.divider()
st.subheader(f"📋 Overzicht {vorm_type} (mm)")
overzicht_data = {"Item": ["Lengte L1", "Lengte L2", "Hoogte H", "Dikte D"], "Waarde": [f"{int(l1)}", f"{int(l2)}", f"{int(h)}", f"{int(dikte) if dikte > 0 else 'N.v.t.'}"]}
for i, px in enumerate(posities_x):
    overzicht_data["Item"].append(f"Zaagsnede X-{i+1}"); overzicht_data["Waarde"].append(f"{int(px)}")
for i, py in enumerate(posities_y):
    overzicht_data["Item"].append(f"Zaagsnede Y-{i+1}"); overzicht_data["Waarde"].append(f"{int(py)}")

st.table(pd.DataFrame(overzicht_data))
