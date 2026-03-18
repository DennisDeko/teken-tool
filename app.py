import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MatplotlibPolygon
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Imports voor PDF generatie
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="DEKO Maatwerk Editor Pro", layout="wide")

# --- DATABASE STANDAARD MATEN ---
steen_maten = {
    "Vrij invoeren": (210, 100, 50),
    "Waalformaat": (210, 100, 50),
    "Dikformaat": (210, 100, 65),
    "Brabantse steen": (180, 88, 53),
    "Deens formaat": (228, 108, 54),
    "IJsselformaat": (160, 78, 41),
    "Vechtformaat": (210, 100, 40)
}

# --- LOGO ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_l, col_r = st.columns([1, 4])
with col_l:
    try: st.image(LOGO_URL, width=150)
    except: st.empty()
with col_r:
    st.title("DEKO Maatwerk Editor Pro")

st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Project Info")
    ref = st.text_input("Referentie", "Project 1")
    aantal = st.number_input("Aantal stuks", 1, 1000, 1)
    st.divider()
    
    def on_format_change():
        st.session_state['ax_count'] = 0

    keuze_naam = st.selectbox("Formaat", list(steen_maten.keys()), on_change=on_format_change)
    std_l, std_b, std_h = steen_maten[keuze_naam]
    vorm_type = st.radio("Type", ["Steen", "Hoek"], horizontal=True)

    with st.expander("Basismaten Steen", expanded=True):
        l1 = st.number_input("Lengte L1 (mm)", value=float(std_l))
        l2 = st.number_input("Breedte L2 (mm)", value=float(std_b))
        h = st.number_input("Hoogte H (mm)", value=float(std_h))
        dikte_hoek = st.number_input("Dikte D (mm)", value=23.0) if vorm_type == "Hoek" else 0.0

    with st.expander("Zaaglijnen (Positie vanaf Links)", expanded=True):
        ax_count = st.slider("Aantal snedes", 0, 5, key='ax_count')
        pos_x = []
        for i in range(ax_count):
            p = st.number_input(f"X{i+1} Positie (mm)", value=23.0 * (i+1), key=f"pos_{i}")
            pos_x.append(p)

# --- LOGICA ---
sorted_x = sorted([px for px in pos_x if 0 < px < l1])
segs_x = [0] + sorted_x + [l1]

# --- 2D VISUALISATIE ---
c_v1, c_v2 = st.columns(2)

with c_v1:
    st.subheader("📐 2D Zaagplan (Gestippelde lijnen)")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_alpha(0)
    
    cols = ['#5bc0de', '#f0ad4e', '#5cb85c', '#d9534f', '#777777']
    
    # Teken segmenten
    for i in range(len(segs_x)-1):
        x_s, x_e = segs_x[i], segs_x[i+1]
        w = x_e - x_s
        c = cols[i % len(cols)]
        
        if w > 0:
            if vorm_type == "Steen":
                ax1.add_patch(plt.Rectangle((x_s, 0), w, l2, facecolor=c, edgecolor='black', alpha=0.7))
                ax1.text(x_s + w/2, l2/2, f"{int(w)}", ha='center', va='center', weight='bold', fontsize=12)
            else:
                if i == 0:
                    p_pts = np.array([[0,0], [x_e,0], [x_e,dikte_hoek], [dikte_hoek,dikte_hoek], [dikte_hoek,l2], [0,l2]])
                    ax1.add_patch(MatplotlibPolygon(p_pts, facecolor=c, edgecolor='black', alpha=0.7))
                    ax1.text(dikte_hoek/2, l2/2, f"{int(w)}", ha='center', va='center', weight='bold', fontsize=12, rotation=90)
                else:
                    y_h = dikte_hoek if x_s >= dikte_hoek else l2
                    ax1.add_patch(plt.Rectangle((x_s, 0), w, y_h, facecolor=c, edgecolor='black', alpha=0.7))
                    ax1.text(x_s + w/2, y_h/2, f"{int(w)}", ha='center', va='center', weight='bold', fontsize=12)

    # Gestippelde Rode Zaaglijnen
    for i, px in enumerate(sorted_x):
        y_max = l2 if (vorm_type=="Steen" or px <= dikte_hoek) else dikte_hoek
        ax1.plot([px, px], [0, y_max], color='red', linestyle='--', linewidth=2, zorder=10)
        ax1.text(px, y_max + 5, f"X{i+1}", color='red', weight='bold', fontsize=14, ha='center')

    ax1.set_xlim(-20, l1+30); ax1.set_ylim(-20, l2+30)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

# --- 3D PREVIEW ---
with c_v2:
    st.subheader("📦 Solide 3D Preview")
    fig3d = go.Figure()

    def add_mesh(fig, x_r, y_r, z_r, color, name):
        if x_r[1] <= x_r[0]: return
        fig.add_trace(go.Mesh3d(
            x=[x_r[0], x_r[1], x_r[1], x_r[0], x_r[0], x_r[1], x_r[1], x_r[0]],
            y=[y_r[0], y_r[0], y_r[1], y_r[1], y_r[0], y_r[0], y_r[1], y_r[1]],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color, flatshading=True, name=name, showscale=False
        ))

    for i in range(len(segs_x)-1):
        xs, xe = segs_x[i], segs_x[i+1]
        c = cols[i % len(cols)]
        if vorm_type == "Steen":
            add_mesh(fig3d, (xs, xe), (0, l2), (0, h), c, f"Deel {i+1}")
        else:
            add_mesh(fig3d, (xs, xe), (0, dikte_hoek), (0, h), c, f"Deel {i+1}")
            if i == 0: add_mesh(fig3d, (0, dikte_hoek), (dikte_hoek, l2), (0, h), c, "Poot")

    fig3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig3d, use_container_width=True)

# --- OVERZICHT ---
st.divider()
overzicht = []
for i, px in enumerate(sorted_x):
    overzicht.append({"Snede": f"X{i+1}", "Positie vanaf Links": f"{px} mm"})

if overzicht:
    st.table(pd.DataFrame(overzicht))
