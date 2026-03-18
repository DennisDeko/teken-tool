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
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- DATABASE STANDAARD MATEN ---
steen_maten = {
    "Vrij invoeren": (210, 100, 50),
    "Waalformaat": (210, 100, 50),
    "Dikformaat / waaldikformaat": (210, 100, 65),
    "Brabantse steen": (180, 88, 53),
    "Deens formaat": (228, 108, 54),
    "Dordtse steen": (180, 88, 43),
    "Dubbel waalformaat": (210, 100, 110),
    "Dunnformat (DF)": (240, 115, 52),
    "Engels formaat": (210, 102.5, 65),
    "Euroformat": (188, 90, 88),
    "F52": (230, 110, 57),
    "Friese drieling": (184, 80, 40),
    "Friese mop": (217, 103, 45),
    "Goudse steen": (155, 72, 53),
    "Groninger steen": (240, 120, 60),
    "Hilversums formaat": (240, 90, 40),
    "IJsselformaat": (160, 78, 41),
    "Juffertje": (175, 82, 40),
    "Kathedraal I": (240, 115, 65),
    "Kathedraal II": (270, 105, 55),
    "Klampmuur-dikformaat": (100, 65, 210),
    "Kloostermop I": (280, 105, 80),
    "Kloostermop II": (320, 130, 80),
    "Lilliput I": (160, 75, 35),
    "Lilliput II": (150, 70, 30),
    "Limburgse steen": (240, 120, 65),
    "Moduul 190-140-90": (190, 140, 90),
    "Moduul 190-90-40": (190, 90, 40),
    "Moduul 190-90-50": (190, 90, 50),
    "Moduul 190-90-90": (190, 90, 90),
    "Moduul 240-90-90": (240, 90, 90),
    "Moduul 290-115-190": (290, 115, 190),
    "Moduul 290-115-90": (290, 115, 90),
    "Moduul 290-90-190": (290, 90, 190),
    "Moduul 290-90-90": (290, 90, 90),
    "Normalformat (NF)": (240, 115, 71),
    "Oldenburgerformat (OF)": (210, 105, 52),
    "Reichsformat (RF)": (240, 115, 61),
    "Rijnformaat": (180, 87, 41),
    "Romeins formaat": (240, 115, 42),
    "Utrechts plat": (215, 102, 38),
    "Vechtformaat": (210, 100, 40),
    "Verblender (2DF)": (240, 115, 113)
}

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_l, col_r = st.columns([1, 4])
with col_l:
    try: st.image(LOGO_URL, width=150)
    except: st.empty()
with col_r:
    st.title("DEKO Maatwerk Editor Pro")

st.divider()

# --- HELPER FUNCTIE: PDF ---
def generate_pdf(df, fig, naam, l, b, h, ref, aantal):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, f"WERKBON: {naam}")
    p.setFont("Helvetica", 11)
    p.drawString(50, 780, f"Referentie: {ref} | Aantal: {aantal} stuks")
    p.drawString(50, 765, f"Afmetingen: {l} x {b} x {h} mm")
    p.line(50, 760, 550, 760)
    
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight', facecolor='white')
    img_buf.seek(0)
    p.drawImage(ImageReader(img_buf), 50, 480, width=450, preserveAspectRatio=True)
    
    p.setFont("Helvetica-Bold", 12); p.drawString(50, 440, "Zaagsnedes Details:")
    y_pos = 420
    p.setFont("Helvetica", 10)
    for _, row in df.iterrows():
        p.drawString(50, y_pos, f"{row['Type']} {row['Nr']}: {row['Vanaf Links']} | {row['Vanaf Rechts']}")
        y_pos -= 15
    p.showPage(); p.save(); buf.seek(0)
    return buf

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
        l1 = st.number_input("L1", value=float(std_l))
        l2 = st.number_input("L2", value=float(std_b))
        h = st.number_input("H", value=float(std_h))
        dikte = st.number_input("Dikte D", value=23.0) if vorm_type == "Hoek" else 0.0

    with st.expander("Snijlijnen", expanded=True):
        ax_count = st.slider("X-snedes", 0, 5, key='ax_count')
        pos_x = [st.number_input(f"X{i+1}", value=23.0 if i==0 else l1-23, key=f"xi_{i}") for i in range(ax_count)]
        ay_count = st.slider("Y-snedes", 0, 5, key='ay_count')
        pos_y = [st.number_input(f"Y{i+1}", value=23.0 if i==0 else l2-23, key=f"yi_{i}") for i in range(ay_count)]

# --- VISUALISATIE ---
sorted_x = sorted([px for px in pos_x if 0 < px < l1])
sorted_y = sorted([py for py in pos_y if 0 < py < l2])

c_v1, c_v2 = st.columns(2)

# --- 2D ZAAGPLAN ---
with c_v1:
    st.subheader("📐 2D Zaagplan (Gezegmenteerd)")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_alpha(0)
    
    # Kleurenpalet voor segmenten
    cols = ['#5bc0de', '#f0ad4e', '#5cb85c', '#d9534f', '#777777']
    segs_x = [0] + sorted_x + [l1]
    
    # Teken segmenten afwisselend gekleurd
    for i in range(len(segs_x)-1):
        x_s, x_e = segs_x[i], segs_x[i+1]
        w = x_e - x_s
        c = cols[i % len(cols)]
        
        if vorm_type == "Steen":
            ax1.add_patch(plt.Rectangle((x_s, 0), w, l2, facecolor=c, edgecolor='black', alpha=0.7))
            ax1.text(x_s + w/2, l2/2, f"{int(w)}", ha='center', va='center', weight='bold', fontsize=10)
        else:
            if i == 0:
                # Hoek basis
                p_pts = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
                ax1.add_patch(MatplotlibPolygon(p_pts, facecolor=c, edgecolor='black', alpha=0.7))
                ax1.text(dikte/2, l2/2, f"Poot", ha='center', rotation=90)
            else:
                y_h = dikte if x_s >= dikte else l2
                ax1.add_patch(plt.Rectangle((x_s, 0), w, y_h, facecolor=c, edgecolor='black', alpha=0.7))
                ax1.text(x_s + w/2, y_h/2, f"{int(w)}", ha='center', va='center', weight='bold')

    # Rode zaaglijnen
    for px in sorted_x:
        y_m = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px - zaag_dikte/2, 0), zaag_dikte, y_m, color='red', zorder=10))
    for py in sorted_y:
        x_m = l1 if (vorm_type=="Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py - zaag_dikte/2), x_m, zaag_dikte, color='red', zorder=10))

    ax1.set_xlim(-20, l1+20); ax1.set_ylim(-20, l2+20)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

# --- 3D PREVIEW ---
with c_v2:
    st.subheader("📦 Solide 3D Preview")
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

    for i in range(len(segs_x)-1):
        x_s = segs_x[i] + (zaag_dikte/2 if i > 0 else 0)
        x_e = segs_x[i+1] - (zaag_dikte/2 if i < len(segs_x)-2 else 0)
        c = cols[i % len(cols)]
        
        if vorm_type == "Steen":
            add_mesh(fig3d, (x_s, x_e), (0, l2), (0, h), c, f"Deel {i+1}")
        else:
            add_mesh(fig3d, (x_s, x_e), (0, dikte), (0, h), c, f"Deel {i+1}")
            if i == 0 and l2 > dikte:
                add_mesh(fig3d, (0, dikte), (dikte, l2), (0, h), c, "Poot")

    for px in sorted_x:
        y_m = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        add_mesh(fig3d, (px-zaag_dikte/2, px+zaag_dikte/2), (0, y_m), (0, h), 'red', "Zaag")

    fig3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig3d, use_container_width=True)

# --- TABEL & PDF ---
st.divider()
data = []
for i, px in enumerate(pos_x): data.append({"Type": "X-Snede", "Nr": i+1, "Vanaf Links": f"{px}mm", "Vanaf Rechts": f"{l1-px}mm"})
for i, py in enumerate(pos_y): data.append({"Type": "Y-Snede", "Nr": i+1, "Vanaf Onder": f"{py}mm", "Vanaf Boven": f"{l2-py}mm"})
df_wb = pd.DataFrame(data)

c1, c2 = st.columns([2, 1])
with c1: st.dataframe(df_wb, use_container_width=True, hide_index=True)
with c2:
    if not df_wb.empty:
        pdf_data = generate_pdf(df_wb, fig1, keuze_naam, l1, l2, h, ref, aantal)
        st.download_button("📄 Download PDF Werkbon", pdf_data, f"Werkbon_{ref}.pdf", "application/pdf")
