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
        st.session_state['ay_count'] = 0

    keuze_naam = st.selectbox("Formaat", list(steen_maten.keys()), on_change=on_format_change)
    std_l, std_b, std_h = steen_maten[keuze_naam]
    vorm_type = st.radio("Type", ["Steen", "Hoek"], horizontal=True)
    zaag_dikte = st.number_input("Zaagdikte (mm)", 0.0, 10.0, 3.0, step=0.5)

    with st.expander("Basismaten Steen", expanded=True):
        l1 = st.number_input("Totale Lengte L1 (mm)", value=float(std_l))
        l2 = st.number_input("Totale Breedte L2 (mm)", value=float(std_b))
        h = st.number_input("Hoogte H (mm)", value=float(std_h))
        dikte_hoek = st.number_input("Dikte D (mm)", value=23.0) if vorm_type == "Hoek" else 0.0

    with st.expander("Netto Snijmaten (Vanaf links)", expanded=True):
        st.caption("Vul hier de gewenste netto maat van de blokjes in.")
        ax_count = st.slider("Aantal snedes", 0, 5, key='ax_count')
        # We slaan de gewenste NETTO maten op
        netto_maten = []
        for i in range(ax_count):
            m = st.number_input(f"Stuk {i+1} Netto Breedte (mm)", value=23.0, key=f"netto_{i}")
            netto_maten.append(m)

# --- CALCULATIE POSITIES ---
# De zaaglijnen worden geplaatst NA de netto maat.
# Snede 1 = Netto 1 + (zaagdikte/2)
# Snede 2 = Netto 1 + Zaagdikte + Netto 2 + (zaagdikte/2)
pos_x_zaag = []
current_pos = 0
for i, m in enumerate(netto_maten):
    snede_centrum = current_pos + m + (zaag_dikte / 2)
    pos_x_zaag.append(snede_centrum)
    current_pos += m + zaag_dikte

# --- 2D VISUALISATIE ---
c_v1, c_v2 = st.columns(2)

with c_v1:
    st.subheader("📐 2D Zaagplan (Input = Netto Maat)")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_alpha(0)
    
    cols = ['#5bc0de', '#f0ad4e', '#5cb85c', '#d9534f', '#777777']
    
    # Teken de segmenten
    start_x = 0
    for i in range(len(netto_maten) + 1):
        c = cols[i % len(cols)]
        
        # Bepaal de breedte van dit segment voor de tekening
        if i < len(netto_maten):
            w_segment = netto_maten[i]
        else:
            # Het laatste reststuk
            w_segment = l1 - current_pos
            if w_segment < 0: w_segment = 0

        if w_segment > 0:
            if vorm_type == "Steen":
                ax1.add_patch(plt.Rectangle((start_x, 0), w_segment, l2, facecolor=c, edgecolor='black', alpha=0.8))
                ax1.text(start_x + w_segment/2, l2/2, f"{w_segment:.1f}", ha='center', va='center', weight='bold', fontsize=12)
            else:
                if i == 0:
                    # Speciale tekening voor hoek (eerste stuk is de hoek zelf)
                    p_pts = np.array([[0,0], [w_segment,0], [w_segment,dikte_hoek], [dikte_hoek,dikte_hoek], [dikte_hoek,l2], [0,l2]])
                    ax1.add_patch(MatplotlibPolygon(p_pts, facecolor=c, edgecolor='black', alpha=0.8))
                    ax1.text(dikte_hoek/2, l2/2, f"{w_segment:.1f}", ha='center', va='center', weight='bold', fontsize=12, rotation=90)
                else:
                    y_h = dikte_hoek if start_x >= dikte_hoek else l2
                    ax1.add_patch(plt.Rectangle((start_x, 0), w_segment, y_h, facecolor=c, edgecolor='black', alpha=0.8))
                    ax1.text(start_x + w_segment/2, y_h/2, f"{w_segment:.1f}", ha='center', va='center', weight='bold', fontsize=12)
        
        start_x += w_segment + zaag_dikte

    # Teken de rode zaagsnedes op de berekende posities
    for i, px in enumerate(pos_x_zaag):
        if px < l1:
            y_m = l2 if (vorm_type=="Steen" or px <= dikte_hoek) else dikte_hoek
            ax1.add_patch(plt.Rectangle((px - zaag_dikte/2, 0), zaag_dikte, y_m, color='red', zorder=10))
            ax1.text(px, y_m + 10, f"X{i+1}", color='red', weight='bold', fontsize=15, ha='center')

    ax1.set_xlim(-20, l1+30); ax1.set_ylim(-20, l2+40)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

# --- 3D PREVIEW ---
with c_v2:
    st.subheader("📦 3D Preview")
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

    start_x_3d = 0
    for i in range(len(netto_maten) + 1):
        w_seg = netto_maten[i] if i < len(netto_maten) else (l1 - start_x_3d)
        if w_seg <= 0: continue
        
        c = cols[i % len(cols)]
        if vorm_type == "Steen":
            add_mesh(fig3d, (start_x_3d, start_x_3d + w_seg), (0, l2), (0, h), c, f"Stuk {i+1}")
        else:
            add_mesh(fig3d, (start_x_3d, start_x_3d + w_seg), (0, dikte_hoek), (0, h), c, f"Stuk {i+1}")
            if i == 0: add_mesh(fig3d, (0, dikte_hoek), (dikte_hoek, l2), (0, h), c, "Hoekpoot")
        
        start_x_3d += w_seg + zaag_dikte

    fig3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig3d, use_container_width=True)

# --- OVERZICHT ---
st.divider()
overzicht = []
for i, px in enumerate(pos_x_zaag):
    overzicht.append({"Snede": f"X{i+1}", "Machine Instelling (Centrum zaag)": f"{px:.1f} mm", "Netto maat blokje": f"{netto_maten[i]} mm"})

if overzicht:
    df_wb = pd.DataFrame(overzicht)
    st.table(df_wb)
