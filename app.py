import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MatplotlibPolygon
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURATIE ---
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

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("Project Info")
    ref = st.text_input("Referentie", "Project A")
    aantal = st.number_input("Aantal stuks", 1, 1000, 1)
    st.divider()
    
    keuze_naam = st.selectbox("Formaat", list(steen_maten.keys()))
    std_l, std_b, std_h = steen_maten[keuze_naam]
    vorm_type = st.radio("Type", ["Steen", "Hoek"], horizontal=True)
    spatiëring = st.slider("Exploded View Afstand (mm)", 0, 30, 10)

    with st.expander("Basismaten", expanded=True):
        l1 = st.number_input("Lengte L1 (X-as)", value=float(std_l))
        l2 = st.number_input("Breedte L2 (Y-as)", value=float(std_b))
        h = st.number_input("Hoogte H", value=float(std_h))
        dikte = st.number_input("Dikte D", value=23.0) if vorm_type == "Hoek" else 0.0

    # Zaaglijnen X
    with st.expander("Zaaglijnen X (Lengte / Ligger)", expanded=True):
        x_count = st.slider("Aantal X-snedes", 0, 5, 1)
        pos_x = [st.number_input(f"X{i+1} Positie (mm)", value=50.0*(i+1), key=f"x{i}") for i in range(x_count)]
    
    # Zaaglijnen Y
    with st.expander("Zaaglijnen Y (Breedte / Poot)", expanded=True):
        y_count = st.slider("Aantal Y-snedes", 0, 5, 0)
        pos_y = [st.number_input(f"Y{i+1} Positie (mm)", value=40.0*(i+1), key=f"y{i}") for i in range(y_count)]

# --- 3. LOGICA ---
sorted_x = sorted([px for px in pos_x if 0 < px < l1])
segs_x = [0] + sorted_x + [l1]

# Voor Y snedes: bij hoek starten we vanaf de dikte D, bij steen vanaf 0
y_start = dikte if vorm_type == "Hoek" else 0
sorted_y = sorted([py for py in pos_y if y_start < py < l2])
segs_y = [y_start] + sorted_y + [l2]

cols = ['#5bc0de', '#f0ad4e', '#5cb85c', '#d9534f', '#9b59b6', '#34495e']

# --- 4. LAYOUT ---
c1, c2 = st.columns(2)

# --- 5. 2D ZAAGPLAN ---
with c1:
    st.subheader("📐 2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_alpha(0)

    # Teken X-segmenten
    for i in range(len(segs_x)-1):
        xs, xe, w = segs_x[i], segs_x[i+1], segs_x[i+1]-segs_x[i]
        c = cols[i % len(cols)]
        h_box = dikte if vorm_type=="Hoek" else l2
        ax1.add_patch(plt.Rectangle((xs, 0), w, h_box, facecolor=c, edgecolor='black', alpha=0.6))
        ax1.text(xs+w/2, h_box/2, f"{int(w)}", ha='center', va='center', weight='bold')

    # Teken Y-segmenten
    if vorm_type == "Hoek":
        for j in range(len(segs_y)-1):
            ys, ye, h_seg = segs_y[j], segs_y[j+1], segs_y[j+1]-segs_y[j]
            c = cols[(len(segs_x) + j) % len(cols)]
            ax1.add_patch(plt.Rectangle((0, ys), dikte, h_seg, facecolor=c, edgecolor='black', alpha=0.6))
            ax1.text(dikte/2, ys+h_seg/2, f"{int(h_seg)}", ha='center', va='center', rotation=90)
    elif y_count > 0:
         for j in range(len(segs_y)-1):
            ys, ye, h_seg = segs_y[j], segs_y[j+1], segs_y[j+1]-segs_y[j]
            c = cols[(len(segs_x) + j) % len(cols)]
            ax1.add_patch(plt.Rectangle((0, ys), l1, h_seg, facecolor=c, edgecolor='black', alpha=0.3))

    # Zaaglijnen tekenen
    for px in sorted_x: 
        y_lim = dikte if vorm_type=="Hoek" else l2
        ax1.plot([px, px], [0, y_lim], "r--", lw=1.5)
    for py in sorted_y: 
        x_lim = dikte if vorm_type=="Hoek" else l1
        ax1.plot([0, x_lim], [py, py], "r--", lw=1.5)

    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1)

# --- 6. 3D VIEW ---
with c2:
    st.subheader("📦 3D Exploded View")
    fig3d = go.Figure()

    def add_mesh(fig, x_r, y_r, z_r, color, off_x=0, off_y=0):
        x0, x1 = x_r[0]+off_x, x_r[1]+off_x
        y0, y1 = y_r[0]+off_y, y_r[1]+off_y
        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0, x0, x1, x1, x0],
            y=[y0, y0, y1, y1, y0, y0, y1, y1],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
            color=color, flatshading=True, showscale=False, opacity=0.9
        ))
        # Zwarte omlijning
        edge_x = [x0, x1, x1, x0, x0, x0, x1, x1, x0, x0, x1, x1, x1, x1, x0, x0]
        edge_y = [y0, y0, y1, y1, y0, y0, y0, y1, y1, y1, y1, y1, y0, y0, y0, y0]
        edge_z = [0, 0, 0, 0, 0, h, h, h, h, 0, 0, h, h, 0, 0, h]
        fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=1)))

    # X-segmenten tekenen (Ligger bij hoek, lengte bij steen)
    for i in range(len(segs_x)-1):
        # Bij een hoek, als dit NIET het eerste segment is (van de poot), is de Y-maat Dikte
        y_m = dikte if vorm_type == "Hoek" else l2
        add_mesh(fig3d, (segs_x[i], segs_x[i+1]), (0, y_m), (0, h), cols[i%6], off_x=i*spatiëring)

    # Y-segmenten tekenen (Poot bij hoek, breedte bij steen)
    if y_count > 0:
        for j in range(len(segs_y)-1):
            if vorm_type == "Hoek":
                x_w = dikte # De poot zit altijd op dikte D
                if segs_y[j] >= y_start:
                    add_mesh(fig3d, (0, x_w), (segs_y[j], segs_y[j+1]), (0, h), cols[(j+3)%6], off_y=j*spatiëring)
            elif segs_y[j] >= y_start:
                    add_mesh(fig3d, (0, l1), (segs_y[j], segs_y[j+1]), (0, h), cols[(j+3)%6], off_y=j*spatiëring)

    fig3d.update_layout(
        scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                   camera=dict(eye=dict(x=1.8, y=1.8, z=1.2)), dragmode=False),
        margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    st.plotly_chart(fig3d, use_container_width=True, config={'displayModeBar': False})

# --- 7. TABEL ---
st.divider()
t1, t2 = st.columns(2)
with t1:
    st.write(f"**Referentie:** {ref} | **Aantal:** {aantal}")
    st.write("**X-Snedes (Lengte)**")
    if sorted_x:
        df_x = pd.DataFrame([{"Label": f"X{i+1}", "Afstand": f"{p} mm"} for i, p in enumerate(sorted_x)])
        st.table(df_x)
    else:
        st.write("Geen horizontale snedes.")

with t2:
    st.write("**Basismaten**")
    st.write(f"L1: {l1} | L2: {l2} | H: {h}" + (f" | Dikte: {dikte}" if vorm_type=="Hoek" else ""))
    st.write("**Y-Snedes (Breedte/Poot)**")
    if sorted_y:
        df_y = pd.DataFrame([{"Label": f"Y{i+1}", "Afstand": f"{p} mm"} for i, p in enumerate(sorted_y)])
        st.table(df_y)
    else:
        st.write("Geen verticale snedes.")
