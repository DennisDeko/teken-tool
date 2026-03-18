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

st.set_page_config(page_title="DEKO Maatwerk Tool Pro", layout="wide")

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

    with st.expander("Maten", expanded=True):
        l1 = st.number_input("L1 (mm)", value=float(std_l))
        l2 = st.number_input("L2 (mm)", value=float(std_b))
        h = st.number_input("H (mm)", value=float(std_h))
        dikte = st.number_input("Dikte D (mm)", value=23.0) if vorm_type == "Hoek" else 0.0

    with st.expander("Snijlijnen", expanded=True):
        ax_count = st.slider("Aantal X-snedes", 0, 5, key='ax_count')
        pos_x = [st.number_input(f"X{i+1} positie", value=23.0 if i==0 else l1-23, key=f"xi_{i}") for i in range(ax_count)]
        ay_count = st.slider("Aantal Y-snedes", 0, 5, key='ay_count')
        pos_y = [st.number_input(f"Y{i+1} positie", value=23.0 if i==0 else l2-23, key=f"yi_{i}") for i in range(ay_count)]

# --- LOGICA: BEREKENING SEGMENTEN MET ZAAGDIKTE ---
sorted_x = sorted([px for px in pos_x if 0 < px < l1])
sorted_y = sorted([py for py in pos_y if 0 < py < l2])

# --- 2D VISUALISATIE ---
c_v1, c_v2 = st.columns(2)

with c_v1:
    st.subheader("📐 2D Zaagplan (Netto maten)")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_alpha(0)
    
    cols = ['#5bc0de', '#f0ad4e', '#5cb85c', '#d9534f', '#777777']
    
    # Teken segmenten (X-as)
    x_points = [0] + sorted_x + [l1]
    for i in range(len(x_points)-1):
        # Visuele start/eind van het blokje (rekening houdend met zaagsnede visueel)
        vis_x_start = x_points[i] + (zaag_dikte/2 if i > 0 else 0)
        vis_x_end = x_points[i+1] - (zaag_dikte/2 if i < len(x_points)-2 else 0)
        
        # NETTO MAAT CALCULATIE:
        # De werkelijke maat van het stuk steen is: (Positie volgende snede - Positie huidige snede) - dikte van de zaagblad-impact
        if i == 0 or i == len(x_points)-2:
            netto_w = (x_points[i+1] - x_points[i]) - (zaag_dikte/2)
        else:
            netto_w = (x_points[i+1] - x_points[i]) - zaag_dikte
        
        if netto_w < 0: netto_w = 0 # Voorkom negatieve getallen bij foutieve invoer
        
        c = cols[i % len(cols)]
        w_vis = x_points[i+1] - x_points[i]
        
        if vorm_type == "Steen":
            ax1.add_patch(plt.Rectangle((x_points[i], 0), w_vis, l2, facecolor=c, edgecolor='black', alpha=0.7))
            # Toon Netto Maat
            ax1.text(x_points[i] + w_vis/2, l2/2, f"{netto_w:.1f}", ha='center', va='center', weight='bold', fontsize=12)
        else:
            if i == 0:
                p_pts = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
                ax1.add_patch(MatplotlibPolygon(p_pts, facecolor=c, edgecolor='black', alpha=0.7))
            else:
                y_h = dikte if x_points[i] >= dikte else l2
                ax1.add_patch(plt.Rectangle((x_points[i], 0), w_vis, y_h, facecolor=c, edgecolor='black', alpha=0.7))
                ax1.text(x_points[i] + w_vis/2, y_h/2, f"{netto_w:.1f}", ha='center', va='center', weight='bold', fontsize=12)

    # Grote Labels voor Zaaglijnen
    for i, px in enumerate(sorted_x):
        y_m = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px - zaag_dikte/2, 0), zaag_dikte, y_m, color='red', zorder=10))
        ax1.text(px, y_m + 8, f"X{i+1}", color='red', weight='bold', fontsize=14, ha='center')

    for i, py in enumerate(sorted_y):
        x_m = l1 if (vorm_type=="Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py - zaag_dikte/2), x_m, zaag_dikte, color='red', zorder=10))
        ax1.text(x_m + 8, py, f"Y{i+1}", color='red', weight='bold', fontsize=14, va='center')

    ax1.set_xlim(-30, l1+40); ax1.set_ylim(-30, l2+40)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

# --- 3D PREVIEW ---
with c_v2:
    st.subheader("📦 3D Preview")
    fig3d = go.Figure()

    def add_mesh(fig, x_r, y_r, z_r, color, name):
        if x_r[1] <= x_r[0] or y_r[1] <= y_r[0]: return
        fig.add_trace(go.Mesh3d(
            x=[x_r[0], x_r[1], x_r[1], x_r[0], x_r[0], x_r[1], x_r[1], x_r[0]],
            y=[y_r[0], y_r[0], y_r[1], y_r[1], y_r[0], y_r[0], y_r[1], y_r[1]],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color, flatshading=True, name=name, showscale=False
        ))

    for i in range(len(x_points)-1):
        xs, xe = x_points[i], x_points[i+1]
        c = cols[i % len(cols)]
        if vorm_type == "Steen":
            add_mesh(fig3d, (xs, xe), (0, l2), (0, h), c, f"Deel {i+1}")
        else:
            add_mesh(fig3d, (xs, xe), (0, dikte), (0, h), c, f"Deel {i+1}")
            if i == 0 and l2 > dikte: add_mesh(fig3d, (0, dikte), (dikte, l2), (0, h), c, "Poot")

    fig3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig3d, use_container_width=True)

# --- PDF GENERATIE FUNCTIE ---
def generate_pdf(df, fig, l, b, h, ref, aantal):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    p.setFont("Helvetica-Bold", 16); p.drawString(50, 800, f"WERKBON: {ref}")
    p.setFont("Helvetica", 11); p.drawString(50, 780, f"Aantal: {aantal} stuks | Maat: {l}x{b}x{h}mm | Zaagdikte: {zaag_dikte}mm")
    p.line(50, 775, 550, 775)
    
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight', facecolor='white')
    img_buf.seek(0)
    p.drawImage(ImageReader(img_buf), 50, 480, width=450, preserveAspectRatio=True)
    
    p.setFont("Helvetica-Bold", 12); p.drawString(50, 440, "Zaaginstellingen (Vanaf rand):")
    y = 420
    p.setFont("Helvetica", 10)
    for _, row in df.iterrows():
        p.drawString(50, y, f"{row['Snede']}: {row['Positie']} mm vanaf rand")
        y -= 15
    p.showPage(); p.save(); buf.seek(0)
    return buf

# --- OVERZICHT ---
st.divider()
overzicht_data = []
for i, px in enumerate(sorted_x): overzicht_data.append({"Snede": f"X{i+1}", "Positie": f"{px}"})
for i, py in enumerate(sorted_y): overzicht_data.append({"Snede": f"Y{i+1}", "Positie": f"{py}"})

if overzicht_data:
    df_wb = pd.DataFrame(overzicht_data)
    c1, c2 = st.columns([2, 1])
    with c1: st.dataframe(df_wb, use_container_width=True, hide_index=True)
    with c2:
        pdf_data = generate_pdf(df_wb, fig1, l1, l2, h, ref, aantal)
        st.download_button("📄 Download PDF Werkbon", pdf_data, f"Werkbon_{ref}.pdf")
