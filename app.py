import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MatplotlibPolygon
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

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
    st.image(LOGO_URL, width=150)
with col_r:
    st.title("DEKO Maatwerk Editor Pro")
    st.caption("Professionele 2D/3D visualisatie en werkbon generatie")

st.divider()

# --- HELPER FUNCTIE: PDF GENERATIE ---
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
    
    # 2D Tekening invoegen
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 100, "Zaagplan 2D")
    img_buffer = BytesIO()
    fig2d.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
    p.drawImage(img_buffer, 50, height - 350, width=300, preserveAspectRatio=True)
    
    # Tabel
    p.drawString(50, height - 380, "Zaagsnedes Details")
    ty = height - 400
    p.setFont("Helvetica-Bold", 10)
    
    # Tabel headers
    cols = ["Type", "Nr", "Vanaf As 1", "Vanaf As 2"]
    x_offsets = [50, 150, 200, 320]
    for i, col in enumerate(cols):
        p.drawString(x_offsets[i], ty, col)
    
    ty -= 20
    p.setFont("Helvetica", 10)
    for index, row in overzicht_df.iterrows():
        if ty < 50: # Nieuwe pagina als tabel te lang is
            p.showPage()
            ty = height - 50
            p.setFont("Helvetica", 10)
            
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

# --- SIDEBAR & LOGICA ---
with st.sidebar:
    st.header("Configuratie")
    
    # Snelkeuze met Session State om posities te resetten bij formaatwijziging
    def on_format_change():
        st.session_state['pos_x'] = []
        st.session_state['pos_y'] = []
        st.session_state['ax_count'] = 0
        st.session_state['ay_count'] = 0

    keuze_naam = st.selectbox("1. Kies standaard maat", list(steen_maten.keys()), on_change=on_format_change)
    std_l, std_b, std_h = steen_maten[keuze_naam]
    
    vorm_type = st.radio("2. Type product", ["Steen", "Hoek"], horizontal=True)
    zaag_dikte = st.number_input("Zaagblad dikte (mm)", 0.0, 10.0, 3.0, step=0.5)

    with st.expander("Afmetingen Aanpassen", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        l1 = col_a.number_input("L1 (mm)", value=float(std_l), step=1.0)
        l2 = col_b.number_input("L2 (mm)", value=float(std_b), step=1.0)
        h = col_c.number_input("H (mm)", value=float(std_h), step=1.0)
        
        if vorm_type == "Hoek":
            dikte = st.number_input("Dikte D (mm)", value=min(23.0, l1/2, l2/2))
            # Validatie dikte
            if dikte >= l1 or dikte >= l2:
                st.error("Dikte D kan niet groter zijn dan L1 of L2.")
                dikte = min(l1, l2) - 1
            grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        else:
            dikte = 0.0
            grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])

    # Zaaglijnen Sectie met Validatie
    with st.expander("Zaaglijnen (Rood)", expanded=True):
        # Initialiseer session state voor zaagsnedes als ze niet bestaan
        if 'ax_count' not in st.session_state: st.session_state['ax_count'] = 0
        if 'ay_count' not in st.session_state: st.session_state['ay_count'] = 0
        if 'pos_x' not in st.session_state: st.session_state['pos_x'] = []
        if 'pos_y' not in st.session_state: st.session_state['pos_y'] = []

        ax_count = st.slider("Aantal X-snedes", 0, 5, key='ax_count')
        pos_x = []
        for i in range(ax_count):
            # Default waarde slim kiezen
            default_x = 23.0 if i == 0 else (l1 - 23.0 if i == 1 else l1 / 2)
            val = st.number_input(f"X{i+1} positie (mm)", value=default_x, key=f"x_in_{i}")
            if val > l1 or val < 0:
                st.warning(f"X{i+1} valt buiten de steen!")
            pos_x.append(val)

        st.markdown("---")
        ay_count = st.slider("Aantal Y-snedes", 0, 5, key='ay_count')
        pos_y = []
        for i in range(ay_count):
            default_y = 23.0 if i == 0 else (l2 - 23.0 if i == 1 else l2 / 2)
            val = st.number_input(f"Y{i+1} positie (mm)", value=default_y, key=f"y_in_{i}")
            if val > l2 or val < 0:
                st.warning(f"Y{i+1} valt buiten de steen!")
            pos_y.append(val)

# --- HOOFDSCHERM VISUALISATIE ---
col_vis1, col_vis2 = st.columns([1, 1])

# --- 2D Zaagplan (Matplotlib) ---
with col_vis1:
    st.subheader("📐 2D Technische Tekening")
    # Gebruik transparante achtergrond voor betere integratie in Streamlit
    fig1, ax1 = plt.subplots(figsize=(6, 5), facecolor='none')
    ax1.set_facecolor('none')
    
    # 1. Teken de basisvorm
    poly = MatplotlibPolygon(grond_poly, facecolor='#eaeaea', alpha=0.7, edgecolor='#333333', linewidth=2, zorder=1)
    ax1.add_patch(poly)

    # 2. Hulplijnen en Zaagsnedes X
    for i, px in enumerate(pos_x):
        if 0 <= px <= l1:
            y_m = l2 if (vorm_type=="Steen" or px<=dikte) else dikte
            # De zaagsnede zelf (Rood vlak)
            ax1.add_patch(plt.Rectangle((px - zaag_dikte/2, 0), zaag_dikte, y_m, facecolor='#d9534f', alpha=0.9, zorder=3))
            # Hulplijn (Stippellijn)
            ax1.plot([px, px], [0, l2 + 15], color='#d9534f', linestyle='--', linewidth=1, zorder=2)
            # Label
            ax1.text(px, l2 + 18, f"X{i+1}", color='#d9534f', weight='bold', fontsize=9, ha='center')

    # 3. Hulplijnen en Zaagsnedes Y
    for i, py in enumerate(pos_y):
        if 0 <= py <= l2:
            x_m = l1 if (vorm_type=="Steen" or py<=dikte) else dikte
            # De zaagsnede zelf (Rood vlak)
            ax1.add_patch(plt.Rectangle((0, py - zaag_dikte/2), x_m, zaag_dikte, facecolor='#d9534f', alpha=0.9, zorder=3))
            # Hulplijn
            ax1.plot([0, l1 + 15], [py, py], color='#d9534f', linestyle='--', linewidth=1, zorder=2)
            # Label
            ax1.text(l1 + 18, py, f"Y{i+1}", color='#d9534f', weight='bold', fontsize=9, va='center')

    # 4. Professionele Maatlijnen (Dimension Lines)
    # L1 (Onder)
    ax1.annotate('', xy=(0, -10), xytext=(l1, -10), arrowprops=dict(arrowstyle='<->', color='black', linewidth=1))
    ax1.text(l1/2, -18, f"{int(l1)} mm", ha='center', fontsize=9, color='black', weight='bold')
    # L2 (Links)
    ax1.annotate('', xy=(-10, 0), xytext=(-10, l2), arrowprops=dict(arrowstyle='<->', color='black', linewidth=1))
    ax1.text(-18, l2/2, f"{int(l2)} mm", va='center', rotation='vertical', fontsize=9, color='black', weight='bold')

    # 5. Assen optimalisatie
    margin = 30
    ax1.set_xlim(-margin, l1 + margin + 10)
    ax1.set_ylim(-margin, l2 + margin + 10)
    ax1.set_aspect('equal')
    ax1.axis('off') # Verberg standaard assen
    
    st.pyplot(fig1, dpi=120, bbox_inches='tight')

# --- 3D Preview (PLOTLY INTERACTIEF) ---
with col_vis2:
    st.subheader("📦 Interactieve 3D Preview")
    
    def get_cube_mesh(pts, height, color, opacity, name):
        # Helper om een gesloten 3D vorm te maken van 2D punten + hoogte
        x, y = pts[:,0], pts[:,1]
        n = len(x)
        zero = np.zeros(n)
        h_arr = np.full(n, height)
        
        # Plotly Mesh3d gebruikt vertices en indices om vlakken te tekenen
        # Dit is complexer dan Matplotlib maar noodzakelijk voor interactie
        
        # Simpele cuboid visualisatie voor snelheid
        x_min, x_max = np.min(x), np.max(x)
        y_min, y_max = np.min(y), np.max(y)
        
        if vorm_type == "Steen" or name != "Basis":
             return go.Mesh3d(
                x=[x_min, x_max, x_max, x_min, x_min, x_max, x_max, x_min],
                y=[y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max],
                z=[0, 0, 0, 0, height, height, height, height],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                opacity=opacity, color=color, name=name, showscale=False
            )
        else:
            # Voor de hoek is een Mesh3d te complex voor deze snelle implementatie
            # We gebruiken hier lijnen om de omtrek te tonen
            pts_3d_low = np.vstack((pts, pts[0]))
            pts_3d_high = np.vstack((pts, pts[0]))
            return go.Scatter3d(
                x=np.concatenate([pts_3d_low[:,0], [None], pts_3d_high[:,0]]),
                y=np.concatenate([pts_3d_low[:,1], [None], pts_3d_high[:,1]]),
                z=np.concatenate([zero, [None], h_arr]),
                mode='lines', line=dict(color=color, width=2), name=name
            )

    fig3d = go.Figure()

    # Basisvorm toevoegen
    if vorm_type == "Steen":
        fig3d.add_trace(get_cube_mesh(grond_poly, h, '#5bc0de', 0.3, "Basis"))
    else:
        # Voor hoek tonen we de outlines
        pts_loop = np.vstack((grond_poly, grond_poly[0]))
        # Onderkant
        fig3d.add_trace(go.Scatter3d(x=pts_loop[:,0], y=pts_loop[:,1], z=pts_loop[:,0]*0, mode='lines', line=dict(color='#5bc0de', width=4), name="Basis Onder"))
        # Bovenkant
        fig3d.add_trace(go.Scatter3d(x=pts_loop[:,0], y=pts_loop[:,1], z=pts_loop[:,0]*0 + h, mode='lines', line=dict(color='#5bc0de', width=4), name="Basis Boven"))
        # Verticale lijnen
        for p in grond_poly:
            fig3d.add_trace(go.Scatter3d(x=[p[0],p[0]], y=[p[1],p[1]], z=[0,h], mode='lines', line=dict(color='#5bc0de', width=2), showlegend=False))

    # Zaagsnedes toevoegen
    for px in pos_x:
        if 0 <= px <= l1:
            y_m = l2 if (vorm_type=="Steen" or px<=dikte) else dikte
            pts_zaag = np.array([[px-zaag_dikte/2, 0], [px+zaag_dikte/2, 0], [px+zaag_dikte/2, y_m], [px-zaag_dikte/2, y_m]])
            fig3d.add_trace(get_cube_mesh(pts_zaag, h, '#d9534f', 0.8, "X-Snede"))

    for py in pos_y:
        if 0 <= py <= l2:
            x_m = l1 if (vorm_type=="Steen" or py<=dikte) else dikte
            pts_zaag = np.array([[0, py-zaag_dikte/2], [x_m, py-zaag_dikte/2], [x_m, py+zaag_dikte/2], [0, py+zaag_dikte/2]])
            fig3d.add_trace(get_cube_mesh(pts_zaag, h, '#d9534f', 0.8, "Y-Snede"))

    # Layout optimalisatie
    max_dim = max(l1, l2, h)
    fig3d.update_layout(
        scene=dict(
            xaxis=dict(title='L1 (mm)', range=[0, max_dim]),
            yaxis=dict(title='L2 (mm)', range=[0, max_dim]),
            zaxis=dict(title='H (mm)', range=[0, max_dim]),
            aspectmode='cube'
        ),
        margin=dict(r=0, l=0, b=0, t=0),
        showlegend=False,
        template="plotly_white"
    )
    
    st.plotly_chart(fig3d, use_container_width=True)

# --- OVERZICHT & EXPORT ---
st.divider()
col_u1, col_u2 = st.columns([2, 1])

with col_u1:
    st.subheader(f"📋 Werkbon Overzicht: {keuze_naam}")
    st.caption(f"Basisformaat: {l1} x {l2} x {h} mm. Zaagbladdikte: {zaag_dikte} mm.")
    overzicht = []
    
    # Assen definiëren voor duidelijke taal op de werkbon
    as1_x, as2_x = "Links", "Rechts"
    as1_y, as2_y = "Onder", "Boven"
    
    for i, px in enumerate(pos_x):
        if 0 <= px <= l1:
            overzicht.append({
                "Type": "X-Snede", 
                "Nr": i+1, 
                "Maat vanaf As 1": f"{px:.1f} mm ({as1_x})", 
                "Maat vanaf As 2": f"{l1-px:.1f} mm ({as2_x})"
            })
    for i, py in enumerate(pos_y):
        if 0 <= py <= l2:
            overzicht.append({
                "Type": "Y-Snede", 
                "Nr": i+1, 
                "Maat vanaf As 1": f"{py:.1f} mm ({as1_y})", 
                "Maat vanaf As 2": f"{l2-py:.1f} mm ({as2_y})"
            })

    if overzicht:
        df_werkbon = pd.DataFrame(overzicht)
        # Styling van de tabel
        st.dataframe(df_werkbon, use_container_width=True, hide_index=True)
    else:
        st.info("Voeg zaaglijnen toe in de sidebar om het overzicht te genereren.")

with col_u2:
    st.subheader("📥 Export")
    st.write("Genereer een PDF werkbon met de tekening en alle maten voor de zagerij.")
    
    if overzicht:
        # PDF Genereren knop
        pdf_buffer = generate_pdf(df_werkbon, fig1, keuze_naam, l1, l2, h)
        
        st.download_button(
            label="📄 Download Werkbon als PDF",
            data=pdf_buffer,
            file_name=f"DEKO_Werkbon_{keuze_naam.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )
    else:
        st.warning("Geen data om te exporteren.")
