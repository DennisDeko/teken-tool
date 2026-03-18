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
col_logo1, col_logo2 = st.columns([1, 4])
with col_logo1:
    try: st.image(LOGO_URL, width=150)
    except: st.empty()
with col_logo2:
    st.title("DEKO Maatwerk Editor Pro")
    st.caption("Professionele Tool voor Maatwerkstenen")

st.divider()

# --- HELPER FUNCTIE: PDF GENERATIE ---
def generate_pdf(df, fig, naam, l, b, h):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, f"WERKBON: {naam} ({l} x {b} x {h} mm)")
    
    # Sla figuur op
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight', facecolor='white')
    img_buf.seek(0)
    p.drawImage(ImageReader(img_buf), 50, 500, width=400, preserveAspectRatio=True)
    
    p.setFont("Helvetica-Bold", 12); p.drawString(50, 480, "Zaagsnedes Details:")
    y_pos = 460
    p.setFont("Helvetica", 10)
    for _, row in df.iterrows():
        p.drawString(50, y_pos, f"{row['Type']} {row['Nr']}: {row['Maat vanaf Links']} | {row['Maat vanaf Rechts']}")
        y_pos -= 15
    
    p.showPage(); p.save(); buf.seek(0)
    return buf

# --- SIDEBAR ---
with st.sidebar:
    st.header("Instellingen")
    
    def on_format_change():
        st.session_state['ax_count'] = 0
        st.session_state['ay_count'] = 0

    keuze_naam = st.selectbox("Standaard maat", list(steen_maten.keys()), on_change=on_format_change)
    std_l, std_b, std_h = steen_maten[keuze_naam]
    
    vorm_type = st.radio("Product type", ["Steen", "Hoek"], horizontal=True)
    zaag_dikte = st.number_input("Zaagdikte (mm)", 0.0, 10.0, 3.0, step=0.5)

    with st.expander("Afmetingen", expanded=True):
        col_dim1, col_dim2, col_dim3 = st.columns(3)
        l1 = col_dim1.number_input("L1 (mm)", value=float(std_l))
        l2 = col_dim2.number_input("L2 (mm)", value=float(std_b))
        h = col_dim3.number_input("H (mm)", value=float(std_h))
        dikte = 0.0
        if vorm_type == "Hoek":
            dikte = st.number_input("Dikte D (mm)", value=min(23.0, l1/2, l2/2))
            grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        else:
            grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])

    with st.expander("Zaagsnedes", expanded=True):
        ax_count = st.slider("X-snedes", 0, 5, key='ax_count')
        pos_x = [st.number_input(f"X{i+1}", value=23.0 if i==0 else l1-23, key=f"xi_{i}") for i in range(ax_count)]
        ay_count = st.slider("Y-snedes", 0, 5, key='ay_count')
        pos_y = [st.number_input(f"Y{i+1}", value=23.0 if i==0 else l2-23, key=f"yi_{i}") for i in range(ay_count)]

# --- VISUALISATIE LOGICA ---
sorted_x = sorted([px for px in pos_x if 0 < px < l1])
sorted_y = sorted([py for py in pos_y if 0 < py < l2])

col_v1, col_v2 = st.columns(2)

# --- 2D ZAAGPLAN ---
with col_v1:
    st.subheader("📐 2D Zaagplan met Maten")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_alpha(0) # Transparant voor Streamlit
    
    # Teken segmenten
    segs_x = [0] + sorted_x + [l1]
    for i in range(len(segs_x)-1):
        x_s, x_e = segs_x[i], segs_x[i+1]
        f_col = '#5bc0de' if i == 0 else '#d3d3d3' # Hoofddeel blauw, rest grijs
        seg_w = x_e - x_s
        
        if vorm_type == "Steen":
            ax1.add_patch(plt.Rectangle((x_s, 0), seg_w, l2, facecolor=f_col, edgecolor='black', alpha=0.5))
            # Segmentmaat binnenin
            ax1.text(x_s + seg_w/2, l2/2, f"{int(seg_w)}", ha='center', va='center', color='black', weight='bold')
        else:
            # Hoek-segmentatie in 2D
            if i == 0:
                poly = MatplotlibPolygon(grond_poly, facecolor='#5bc0de', edgecolor='black', alpha=0.5)
                ax1.add_patch(poly)
                # Hoofddeelmaat L1-D
                ax1.text(dikte + (l1-dikte)/2, dikte/2, f"{int(l1-dikte)}", ha='center', va='center', color='black', weight='bold')
            else:
                y_h = dikte if x_s >= dikte else l2
                ax1.add_patch(plt.Rectangle((x_s, 0), seg_w, y_h, facecolor='#d3d3d3', edgecolor='black', alpha=0.5))
                # Segmentmaat reststuk
                ax1.text(x_s + seg_w/2, y_h/2, f"{int(seg_w)}", ha='center', va='center', color='black', weight='bold')

    # Zaaglijnen
    for i, px in enumerate(sorted_x):
        y_m = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px - zaag_dikte/2, 0), zaag_dikte, y_m, color='red', zorder=10))
        # Zaaglijnlabel X
        ax1.text(px, y_m + 5, f"X{i+1}: {int(px)}", color='red', weight='bold', fontsize=8, ha='center')
    
    for i, py in enumerate(sorted_y):
        x_m = l1 if (vorm_type=="Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py - zaag_dikte/2), x_m, zaag_dikte, color='red', zorder=10))
        # Zaaglijnlabel Y
        ax1.text(x_m + 5, py, f"Y{i+1}: {int(py)}", color='red', weight='bold', fontsize=8, va='center')

    # Maatlijnen (Dimension Lines)
    # L1 (Onder)
    ax1.annotate('', xy=(0, -10), xytext=(l1, -10), arrowprops=dict(arrowstyle='<->', color='black', linewidth=1))
    ax1.text(l1/2, -18, f"L1: {int(l1)}", ha='center', fontsize=9, color='black', weight='bold')
    
    # L2 (Links)
    ax1.annotate('', xy=(-10, 0), xytext=(-10, l2), arrowprops=dict(arrowstyle='<->', color='black', linewidth=1))
    ax1.text(-18, l2/2, f"L2: {int(l2)}", va='center', rotation=90, fontsize=9, color='black', weight='bold')
    
    # H (Optioneel, rechtsboven)
    ax1.annotate('', xy=(l1+10, l2), xytext=(l1+10, l2+10), arrowprops=dict(arrowstyle='<->', color='black', linewidth=1))
    ax1.text(l1+15, l2+5, f"H: {int(h)}", va='center', fontsize=9, color='black', weight='bold')
    
    if vorm_type == "Hoek":
        # Dikte D (Onder L1-D)
        ax1.annotate('', xy=(0, -5), xytext=(dikte, -5), arrowprops=dict(arrowstyle='<->', color='black', linewidth=1))
        ax1.text(dikte/2, -13, f"D: {int(dikte)}", ha='center', fontsize=8, color='black', weight='bold')

    ax1.set_xlim(-30, l1+30); ax1.set_ylim(-30, l2+30)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

# --- 3D PREVIEW ---
with col_v2:
    st.subheader("📦 3D Preview met Maten")
    fig3d = go.Figure()

    def add_cube(fig, x_r, y_r, z_r, color, name, op=0.9):
        if x_r[1] <= x_r[0] or y_r[1] <= y_r[0]: return
        fig.add_trace(go.Mesh3d(
            x=[x_r[0], x_r[1], x_r[1], x_r[0], x_r[0], x_r[1], x_r[1], x_r[0]],
            y=[y_r[0], y_r[0], y_r[1], y_r[1], y_r[0], y_r[0], y_r[1], y_r[1]],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color, opacity=op, flatshading=True, name=name
        ))

    # Segmentatie X
    curr_x = 0
    for i, next_x in enumerate(segs_x[1:]):
        c = '#5bc0de' if i == 0 else '#f0ad4e'
        s_x = curr_x + (zaag_dikte/2 if curr_x > 0 else 0)
        e_x = next_x - (zaag_dikte/2 if next_x < l1 else 0)
        seg_w = e_x - s_x
        
        if vorm_type == "Steen":
            add_cube(fig3d, (s_x, e_x), (0, l2), (0, h), c, f"Seg {i+1}: {int(seg_w)}")
        else:
            add_cube(fig3d, (s_x, e_x), (0, dikte), (0, h), c, f"Deel X {i+1}: {int(seg_w)}")
            if i == 0 and l2 > dikte:
                add_cube(fig3d, (0, dikte), (dikte, l2), (0, h), c, f"Deel Y: {int(l2)}")
        curr_x = next_x

    # Zaagsnedes Rood
    for px in sorted_x:
        y_m = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        add_cube(fig3d, (px-zaag_dikte/2, px+zaag_dikte/2), (0, y_m), (0, h), 'red', "Zaag X", 1.0)
    for py in sorted_y:
        x_m = l1 if (vorm_type=="Steen" or py <= dikte) else dikte
        add_cube(fig3d, (0, x_m), (py-zaag_dikte/2, py+zaag_dikte/2), (0, h), 'red', "Zaag Y", 1.0)

    fig3d.update_layout(
        scene=dict(
            xaxis_title=f"L1: {int(l1)}",
            yaxis_title=f"L2: {int(l2)}",
            zaxis_title=f"H: {int(h)}",
            aspectmode='data'
        ),
        margin=dict(l=0,r=0,b=0,t=0)
    )
    st.plotly_chart(fig3d, use_container_width=True)

# --- OVERZICHT ---
st.divider()
data = []
for i, px in enumerate(pos_x): data.append({"Type": "X-Snede", "Nr": i+1, "Maat vanaf Links": f"{px}mm", "Maat vanaf Rechts": f"{l1-px}mm", "Segment": "Hoofddeel" if px == min(pos_x) else f"Deel {i+1}"})
for i, py in enumerate(pos_y): data.append({"Type": "Y-Snede", "Nr": i+1, "Maat vanaf Links": f"{py}mm", "Maat vanaf Rechts": f"{l2-py}mm", "Segment": "Y-Deel"})
df_wb = pd.DataFrame(data)

c1, c2 = st.columns([2, 1])
with c1: st.dataframe(df_wb, use_container_width=True, hide_index=True)
with c2:
    if not df_wb.empty:
        # Genereer PDF data
        pdf_data = generate_pdf(df_wb, fig1, keuze_naam, l1, l2, h)
        st.download_button("📄 Download PDF Werkbon", pdf_data, f"Werkbon_{keuze_naam}.pdf", "application/pdf")
