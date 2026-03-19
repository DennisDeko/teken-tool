import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MatplotlibPolygon
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATIE & MATEN ---
steen_maten = {
    "Vrij invoeren": (210, 100, 50),
    "Waalformaat": (210, 100, 50),
    "Dikformaat": (210, 100, 65),
    "Brabantse steen": (180, 88, 53),
    "Deens formaat": (228, 108, 54),
    "IJsselformaat": (160, 78, 41),
    "Vechtformaat": (210, 100, 40)
}

st.set_page_config(page_title="DEKO Maatwerk Tool Pro", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Project Info")
    ref = st.text_input("Referentie", "Project A")
    aantal = st.number_input("Aantal stuks", 1, 1000, 1)
    st.divider()
    
    keuze_naam = st.selectbox("Formaat", list(steen_maten.keys()))
    std_l, std_b, std_h = steen_maten[keuze_naam]
    vorm_type = st.radio("Type", ["Steen", "Hoek"], horizontal=True)
    
    # Visuele ruimte tussen 3D segmenten
    spatiëring = st.slider("3D Segment afstand (mm)", 0, 20, 5)

    with st.expander("Basismaten", expanded=True):
        l1 = st.number_input("Lengte L1 (mm)", value=float(std_l))
        l2 = st.number_input("Breedte L2 (mm)", value=float(std_b))
        h = st.number_input("Hoogte H (mm)", value=float(std_h))
        dikte_hoek = st.number_input("Dikte D (mm)", value=23.0) if vorm_type == "Hoek" else 0.0

    with st.expander("Zaaglijnen", expanded=True):
        ax_count = st.slider("Aantal snedes", 0, 5, value=1)
        pos_x = []
        for i in range(ax_count):
            p = st.number_input(f"X{i+1} Positie (mm)", value=50.0 * (i+1), key=f"pos_{i}")
            pos_x.append(p)

# --- LOGICA ---
# Filter zaaglijnen die binnen de steen vallen
sorted_x = sorted([px for px in pos_x if 0 < px < l1])
segs_x = [0] + sorted_x + [l1]
cols = ['#5bc0de', '#f0ad4e', '#5cb85c', '#d9534f', '#9b59b6']

# --- VISUALISATIE ---
c1, c2 = st.columns(2)

# --- 2D ZAAGPLAN (MATPLOTLIB) ---
with c1:
    st.subheader("📐 2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_alpha(0)
    
    for i in range(len(segs_x)-1):
        x_s, x_e = segs_x[i], segs_x[i+1]
        w = x_e - x_s
        c = cols[i % len(cols)]
        
        if vorm_type == "Steen":
            ax1.add_patch(plt.Rectangle((x_s, 0), w, l2, facecolor=c, edgecolor='black', alpha=0.7))
            ax1.text(x_s + w/2, l2/2, f"{int(w)}", ha='center', va='center', weight='bold', fontsize=12)
        else:
            if i == 0:
                p_pts = np.array([[0,0], [x_e,0], [x_e,dikte_hoek], [dikte_hoek,dikte_hoek], [dikte_hoek,l2], [0,l2]])
                ax1.add_patch(MatplotlibPolygon(p_pts, facecolor=c, edgecolor='black', alpha=0.7))
                ax1.text(dikte_hoek/2, l2/2, f"{int(w)}", ha='center', va='center', weight='bold', fontsize=12)
            else:
                y_h = dikte_hoek if x_s >= dikte_hoek else l2
                ax1.add_patch(plt.Rectangle((x_s, 0), w, y_h, facecolor=c, edgecolor='black', alpha=0.7))
                ax1.text(x_s + w/2, y_h/2, f"{int(w)}", ha='center', va='center', weight='bold', fontsize=12)

    # Gestippelde zaaglijnen
    for i, px in enumerate(sorted_x):
        y_max = l2 if (vorm_type=="Steen" or px <= dikte_hoek) else dikte_hoek
        ax1.plot([px, px], [0, y_max], color='red', linestyle='--', linewidth=2)
        ax1.text(px, y_max + 5, f"X{i+1}", color='red', weight='bold', fontsize=14, ha='center')

    ax1.set_aspect('equal')
    ax1.axis('off')
    st.pyplot(fig1)

# --- 3D EXPLODED VIEW (PLOTLY - STATISCH) ---
with c2:
    st.subheader("📦 3D Exploded View")
    fig3d = go.Figure()

    def add_box(fig, x_range, y_range, z_range, color, name, offset_x):
        x0, x1 = x_range[0] + offset_x, x_range[1] + offset_x
        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0, x0, x1, x1, x0],
            y=[y_range[0], y_range[0], y_range[1], y_range[1], y_range[0], y_range[0], y_range[1], y_range[1]],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], 
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], 
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color, flatshading=True, name=name, showscale=False, opacity=0.9
        ))

    for i in range(len(segs_x)-1):
        xs, xe = segs_x[i], segs_x[i+1]
        current_offset = i * spatiëring 
        c = cols[i % len(cols)]
        
        if vorm_type == "Steen":
            add_box(fig3d, (xs, xe), (0, l2), (0, h), c, f"Deel {i+1}", current_offset)
        else:
            add_box(fig3d, (xs, xe), (0, dikte_hoek), (0, h), c, f"Deel {i+1}", current_offset)
            if i == 0: 
                add_box(fig3d, (0, dikte_hoek), (dikte_hoek, l2), (0, h), c, "Poot", current_offset)

    # Vaste camerapositie en uitschakelen van interactie
    fig3d.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.2) # Schuine hoek van bovenaf
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )

    # staticPlot=True zorgt ervoor dat de 3D view niet draait of zoomt (lichter voor de browser)
    st.plotly_chart(fig3d, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

# --- TABEL OVERZICHT ---
st.divider()
st.write(f"### Samenvatting: {ref}")
col_a, col_b = st.columns(2)
with col_a:
    st.write(f"**Aantal:** {aantal} stuks")
    st.write(f"**Basisformaat:** {keuze_naam} ({l1}x{l2}x{h} mm)")
with col_b:
    if sorted_x:
        df = pd.DataFrame([{"Snede": f"X{i+1}", "Positie": f"{px} mm"} for i, px in enumerate(sorted_x)])
        st.table(df)
    else:
        st.info("Geen actieve zaaglijnen binnen de lengte van de steen.")
