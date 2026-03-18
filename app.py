import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MatplotlibPolygon
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Belangrijke extra imports voor de PDF fix
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
    try:
        st.image(LOGO_URL, width=150)
    except:
        st.warning("Logo niet gevonden")
with col_logo2:
    st.title("DEKO Maatwerk Editor Pro")
    st.caption("Interactieve 3D visualisatie & Automatische Werkbonnen")

st.divider()

# --- PDF GENERATIE FUNCTIE (GEFIXT) ---
def generate_pdf(overzicht_df, fig2d, keuze_naam, l1, l2, h):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"WERKBON: {keuze_naam}")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 65, f"Afmetingen basis: {l1} x {l2} x {h} mm")
    p.line(50, height - 75, width - 50, height - 75)
    
    # 2D Tekening toevoegen via ImageReader (De Fix)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 100, "Zaagplan 2D")
    
    img_buffer = BytesIO()
    fig2d.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
    img_buffer.seek(0)
    
    try:
        afbeelding = ImageReader(img_buffer)
        p.drawImage(afbeelding, 50, height - 350, width=300, preserveAspectRatio=True)
    except Exception as e:
        p.drawString(50, height - 150, f"Fout bij laden afbeelding: {e}")
    
    # Tabel met maten
    p.drawString(50, height - 380, "Zaagsnedes Details")
    ty = height - 400
    p.setFont("Helvetica-Bold", 10)
    
    cols = ["Type", "Nr", "Vanaf As 1", "Vanaf As 2"]
    x_offsets = [50, 120, 200, 350]
    for i, col in enumerate(cols):
        p.drawString(x_offsets[i], ty, col)
    
    ty -= 20
    p.setFont("Helvetica", 10)
    for index, row in overzicht_df.iterrows():
        if ty < 50:
            p.showPage()
            ty = height - 50
        p.drawString(x_offsets[0], ty, str(row['Type']))
        p.drawString(x_offsets[1], ty, str(row['Nr']))
        p.drawString(x_offsets[2], ty, str(row['Maat vanaf As 1']))
        p.drawString(x_offsets[3], ty, str(row['Maat vanaf As 2']))
        p.line(50, ty-5, width-50, ty-5)
        ty -= 20
        
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- SIDEBAR CONFIGURATIE ---
with st.sidebar:
    st.header("Configuratie")
    
    def reset_cuts():
        st.session_state['ax_count'] = 0
        st.session_state['ay_count'] = 0

    keuze_naam = st.selectbox("1. Kies standaard maat", list(steen_maten.keys()), on_change=reset_cuts)
    std_l, std_b, std_h = steen_maten[keuze_naam]
    
    vorm_type = st.radio("2. Type product", ["Steen", "Hoek"], horizontal=True)
    zaag_dikte = st.number_input("Zaagblad dikte (mm)", 0.0, 10.0, 3.0)

    with st.expander("Afmetingen (mm)", expanded=True):
        l1 = st.number_input("Lengte L1", value=float(std_l))
        l2 = st.number_input("Breedte L2", value=float(std_b))
        h = st.number_input("Hoogte H", value=float(std_h))
        
        dikte = 0.0
        if vorm_type == "Hoek":
            dikte = st.number_input("Dikte D", value=min(23.0, l1/2, l2/2))
            grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        else:
            grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])

    with st.expander("Zaaglijnen", expanded=True):
        ax_count = st.slider("Aantal X-snedes", 0, 5, key='ax_count')
        pos_x = [st.number_input(f"X{i+1}", value=23.0 if i==0 else l1-23, key=f"xi_{i}") for i in range(ax_count)]
        
        ay_count = st.slider("Aantal Y-snedes", 0, 5, key='ay_count')
        pos_y = [st.number_input(f"Y{i+1}", value=23.0 if i==0 else l2-23, key=f"yi_{i}") for i in range(ay_count)]

# --- VISUALISATIE ---
col_2d, col_3d = st.columns(2)

with col_2d:
    st.subheader("📐 2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(5, 5), facecolor='none')
    ax1.set_facecolor('none')
    
    # Basisvorm
    p_patch = MatplotlibPolygon(grond_poly, facecolor='#d3d3d3', alpha=0.6, edgecolor='black', lw=2)
    ax1.add_patch(p_patch)

    # X-snedes tekenen
    for i, px in enumerate(pos_x):
        y_lim = l2 if (vorm_type=="Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px - zaag_dikte/2, 0), zaag_dikte, y_lim, color='red', alpha=0.7))
        ax1.text(px, y_lim + 5, f"X{i+1}", color='red', weight='bold', ha='center')

    # Y-snedes tekenen
    for i, py in enumerate(pos_y):
        x_lim = l1 if (vorm_type=="Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py - zaag_dikte/2), x_lim, zaag_dikte, color='red', alpha=0.7))
        ax1.text(x_lim + 5, py, f"Y{i+1}", color='red', weight='bold', va='center')

    # Maatlijnen L1 & L2
    ax1.annotate('', xy=(0, -10), xytext=(l1, -10), arrowprops=dict(arrowstyle='<->'))
    ax1.text(l1/2, -20, f"{l1}mm", ha='center')
    ax1.annotate('', xy=(-10, 0), xytext=(-10, l2), arrowprops=dict(arrowstyle='<->'))
    ax1.text(-25, l2/2, f"{l2}mm", rotation=90, va='center')

    ax1.set_xlim(-40, l1 + 40); ax1.set_ylim(-40, l2 + 40)
    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

with col_3d:
    st.subheader("📦 3D Preview")
    fig3d = go.Figure()
    
    # Simpele 3D weergave via Plotly lijnen (zeer stabiel)
    if vorm_type == "Steen":
        # Box tekenen
        fig3d.add_trace(go.Mesh3d(x=[0,l1,l1,0,0,l1,l1,0], y=[0,0,l2,l2,0,0,l2,l2], z=[0,0,0,0,h,h,h,h], 
                                 alphahull=0, opacity=0.2, color='cyan'))
    else:
        # Hoek tekenen via Scatter3d lijnen
        p_loop = np.vstack((grond_poly, grond_poly[0]))
        fig3d.add_trace(go.Scatter3d(x=p_loop[:,0], y=p_loop[:,1], z=p_loop[:,0]*0, mode='lines', line=dict(color='black')))
        fig3d.add_trace(go.Scatter3d(x=p_loop[:,0], y=p_loop[:,1], z=p_loop[:,0]*0 + h, mode='lines', line=dict(color='black')))

    fig3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig3d, use_container_width=True)

# --- TABEL & PDF EXPORT ---
st.divider()
overzicht = []
for i, px in enumerate(pos_x):
    overzicht.append({"Type": "X-Snede", "Nr": i+1, "Maat vanaf As 1": f"{px} mm (Links)", "Maat vanaf As 2": f"{l1-px} mm (Rechts)"})
for i, py in enumerate(pos_y):
    overzicht.append({"Type": "Y-Snede", "Nr": i+1, "Maat vanaf As 1": f"{py} mm (Onder)", "Maat vanaf As 2": f"{l2-py} mm (Boven)"})

df_wb = pd.DataFrame(overzicht)
c1, c2 = st.columns([2, 1])

with c1:
    st.table(df_wb if not df_wb.empty else pd.DataFrame(columns=["Info"], data=[["Geen snedes ingevoerd"]]))

with c2:
    if not df_wb.empty:
        pdf_file = generate_pdf(df_wb, fig1, keuze_naam, l1, l2, h)
        st.download_button("📄 Download PDF Werkbon", data=pdf_file, file_name=f"Werkbon_{keuze_naam}.pdf", mime="application/pdf")
