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
    except: st.warning("Logo niet gevonden")
with col_r:
    st.title("DEKO Maatwerk Editor Pro")
    st.caption("Visuele segmentatie: Hoofddeel vs. Reststukken")

st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuratie")
    
    def on_format_change():
        st.session_state['ax_count'] = 0
        st.session_state['ay_count'] = 0

    keuze_naam = st.selectbox("1. Kies standaard maat", list(steen_maten.keys()), on_change=on_format_change)
    std_l, std_b, std_h = steen_maten[keuze_naam]
    
    vorm_type = st.radio("2. Type product", ["Steen", "Hoek"], horizontal=True)
    zaag_dikte = st.number_input("Zaagblad dikte (mm)", 0.0, 10.0, 3.0, step=0.5)

    with st.expander("Afmetingen Aanpassen", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        l1 = col_a.number_input("L1 (mm)", value=float(std_l))
        l2 = col_b.number_input("L2 (mm)", value=float(std_b))
        h = col_c.number_input("H (mm)", value=float(std_h))
        
        dikte = 0.0
        if vorm_type == "Hoek":
            dikte = st.number_input("Dikte D (mm)", value=min(23.0, l1/2, l2/2))
            grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        else:
            grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])

    with st.expander("Zaaglijnen", expanded=True):
        ax_count = st.slider("Aantal X-snedes", 0, 5, key='ax_count')
        pos_x = [st.number_input(f"X{i+1}", value=23.0 if i==0 else l1-23, key=f"xi_{i}") for i in range(ax_count)]
        
        ay_count = st.slider("Aantal Y-snedes", 0, 5, key='ay_count')
        pos_y = [st.number_input(f"Y{i+1}", value=23.0 if i==0 else l2-23, key=f"yi_{i}") for i in range(ay_count)]

# --- VISUALISATIE LOGICA ---
col_v1, col_v2 = st.columns(2)

# Sorteer snedes voor segmentatie
sorted_x = sorted([px for px in pos_x if 0 < px < l1])
sorted_y = sorted([py for py in pos_y if 0 < py < l2])

# --- 2D ZAAGPLAN ---
with col_v1:
    st.subheader("📐 2D Zaagplan (Gekleurd)")
    fig1, ax1 = plt.subplots(figsize=(6, 5), facecolor='none')
    ax1.set_facecolor('none')
    
    # Teken segmenten in verschillende kleuren
    segs_x = [0] + sorted_x + [l1]
    for i in range(len(segs_x)-1):
        x_start = segs_x[i]
        x_end = segs_x[i+1]
        face_col = '#eaeaea' if i == 0 else '#dcdcdc' # Hoofddeel vs reststuk
        edge_col = '#333333'
        
        if vorm_type == "Steen":
            ax1.add_patch(plt.Rectangle((x_start, 0), x_end-x_start, l2, facecolor=face_col, edgecolor=edge_col, lw=1.5))
        else:
            # Voor hoekvorm is segmentatie complexer in 2D, we tekenen de basis en kleuren de reststukken eroverheen
            if i == 0:
                poly = MatplotlibPolygon(grond_poly, facecolor='#eaeaea', edgecolor='#333333', lw=1.5)
                ax1.add_patch(poly)
            else:
                y_h = dikte if x_start >= dikte else l2
                ax1.add_patch(plt.Rectangle((x_start, 0), x_end-x_start, y_h, facecolor='#dcdcdc', edgecolor='#333333', lw=1.5))

    # Zaaglijnen (Rood)
    for px in sorted_x:
        y_m = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px - zaag_dikte/2, 0), zaag_dikte, y_m, color='red', zorder=5))
    for py in sorted_y:
        x_m = l1 if (vorm_type=="Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py - zaag_dikte/2), x_m, zaag_dikte, color='red', zorder=5))

    ax1.set_xlim(-20, l1+20); ax1.set_ylim(-20, l2+20)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

# --- 3D PREVIEW ---
with col_v2:
    st.subheader("📦 3D Preview (Gekleurd)")
    fig3d = go.Figure()

    def add_cube(fig, x_r, y_r, z_r, color, name):
        if x_r[1] <= x_r[0] or y_r[1] <= y_r[0]: return
        fig.add_trace(go.Mesh3d(
            x=[x_r[0], x_r[1], x_r[1], x_r[0], x_r[0], x_r[1], x_r[1], x_r[0]],
            y=[y_r[0], y_r[0], y_r[1], y_r[1], y_r[0], y_r[0], y_r[1], y_r[1]],
            z=[z_r[0], z_r[0], z_r[0], z_r[0], z_r[1], z_r[1], z_r[1], z_r[1]],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color, opacity=0.9, flatshading=True, name=name
        ))

    # X-Segmentatie 3D
    current_x = 0
    for i, next_x in enumerate(segs_x[1:]):
        c = '#5bc0de' if i == 0 else '#f0ad4e' # Blauw vs Oranje
        s_x = current_x + (zaag_dikte/2 if current_x > 0 else 0)
        e_x = next_x - (zaag_dikte/2 if next_x < l1 else 0)
        
        if vorm_type == "Steen":
            add_cube(fig3d, (s_x, e_x), (0, l2), (0, h), c, f"Deel {i+1}")
        else:
            add_cube(fig3d, (s_x, e_x), (0, dikte), (0, h), c, f"Deel {i+1}")
            if i == 0 and l2 > dikte:
                add_cube(fig3d, (0, dikte), (dikte, l2), (0, h), c, "Hoekpoot")
        current_x = next_x

    # Zaagsnedes (Rood)
    for px in sorted_x:
        y_m = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        add_cube(fig3d, (px-zaag_dikte/2, px+zaag_dikte/2), (0, y_m), (0, h), 'red', "Zaagsnede")

    fig3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig3d, use_container_width=True)

# --- PDF GENERATIE ---
def generate_pdf(df, fig, naam, l, b, h):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, f"WERKBON: {naam} ({l}x{b}x{h}mm)")
    
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight', white_background=True)
    img_buf.seek(0)
    p.drawImage(ImageReader(img_buf), 50, 500, width=400, preserveAspectRatio=True)
    
    p.setFont("Helvetica-Bold", 12); p.drawString(50, 480, "Zaagsnedes:")
    y = 460
    p.setFont("Helvetica", 10)
    for _, r in df.iterrows():
        p.drawString(50, y, f"{r['Type']} {r['Nr']}: {r['Maat vanaf As 1']} | {r['Maat vanaf As 2']}")
        y -= 20
    p.showPage(); p.save(); buf.seek(0)
    return buf

# --- OVERZICHT ---
st.divider()
overzicht = []
for i, px in enumerate(pos_x): overzicht.append({"Type": "X-Snede", "Nr": i+1, "Maat vanaf As 1": f"{px}mm (L)", "Maat vanaf As 2": f"{l1-px}mm (R)"})
for i, py in enumerate(pos_y): overzicht.append({"Type": "Y-Snede", "Nr": i+1, "Maat vanaf As 1": f"{py}mm (O)", "Maat vanaf As 2": f"{l2-py}mm (B)"})
df_wb = pd.DataFrame(overzicht)

c_t, c_d = st.columns([2, 1])
with c_t: st.dataframe(df_wb, use_container_width=True, hide_index=True)
with c_d:
    if not df_wb.empty:
        st.download_button("📄 Download PDF", generate_pdf(df_wb, fig1, keuze_naam, l1, l2, h), f"Werkbon_{keuze_naam}.pdf")
