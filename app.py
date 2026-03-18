import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

st.set_page_config(page_title="DEKO Productie Tool", layout="wide")

# --- DATABASE ---
steen_maten = {"Vrij invoeren": (210, 100, 50), "Waalformaat": (210, 100, 50), "Dikformaat": (210, 100, 65)}

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Basis Steen")
    keuze = st.selectbox("Formaat", list(steen_maten.keys()))
    L, B, H = st.number_input("Lengte", value=float(steen_maten[keuze][0])), st.number_input("Breedte", value=float(steen_maten[keuze][1])), st.number_input("Hoogte", value=float(steen_maten[keuze][2]))
    
    st.header("2. Transformatie")
    type_trans = st.selectbox("Type", ["Strippen", "Koppen", "Sparren", "Afkorten", "Hoeken", "Bakjes (L-Vorm)", "Zool", "Lomkop", "Romkop"])
    
    # Specifieke opties per type
    optie = None
    if type_trans in ["Strippen", "Koppen"]:
        optie = st.radio("Aantal", ["1-zijdig", "2-zijdig"])
    
    dikte = st.number_input("Zaag/Strip dikte (mm)", value=23.0)
    zaagblad = st.slider("Zaagblad (mm)", 0.0, 5.0, 3.0)

# --- LOGICA ENGINE ---
def get_geometry(type_t, L, B, H, d, opt, zb):
    product_vlakken = []
    zaaglijnen_2d = [] # [(x, y, breedte, hoogte)]
    
    if type_t == "Strippen":
        # Strippen zaag je in de lengte (B-as)
        zaaglijnen_2d.append((0, d, L, zb))
        if opt == "2-zijdig":
            zaaglijnen_2d.append((0, B - d - zb, L, zb))
            
    elif type_t == "Koppen":
        # Koppen zaag je op de korte kant (L-as)
        zaaglijnen_2d.append((d, 0, zb, B))
        if opt == "2-zijdig":
            zaaglijnen_2d.append((L - d - zb, 0, zb, B))
            
    elif type_t == "Sparren":
        # Sparren is horizontaal (H-as), in 2D bovenaanzicht zie je dit als een vlak-bewerking
        zaaglijnen_2d.append((0, 0, L, B)) # Hele vlak wordt geraakt
        
    elif type_t == "Zool":
        # Zool zaagt in de dikte (H-as)
        zaaglijnen_2d.append((0, 0, L, B))
        
    elif type_t == "Bakjes (L-Vorm)":
        # L-vorm: Strip + Zool
        profiel = [(0,0), (L,0), (L,d), (d,d), (d,B), (0,B)]
        # 3D vertices maken voor L-vorm
        z = [[p[0], p[1], 0] for p in profiel] + [[p[0], p[1], H] for p in profiel]
        idx = [[0,1,2,3,4,5], [6,7,8,9,10,11], [0,1,7,6], [1,2,8,7], [2,3,9,8], [3,4,10,9], [4,5,11,10], [5,0,6,11]]
        product_vlakken = [[z[i] for i in face] for face in idx]

    return zaaglijnen_2d, product_vlakken

zaag_2d, prod_3d = get_geometry(type_trans, L, B, H, dikte, optie, zaagblad)

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan (Bovenaanzicht)")
    fig1, ax1 = plt.subplots()
    ax1.add_patch(plt.Rectangle((0,0), L, B, color='lightgray', alpha=0.3, edgecolor='black'))
    
    for (x, y, w, h_z) in zaag_2d:
        ax1.add_patch(plt.Rectangle((x, y), w, h_z, color='red', alpha=0.8))
    
    if type_trans == "Bakjes (L-Vorm)":
        profiel = plt.Polygon([(0,0), (L,0), (L,dikte), (dikte,dikte), (dikte,B), (0,B)], color='cyan', alpha=0.5)
        ax1.add_patch(profiel)

    ax1.set_xlim(-10, L+10); ax1.set_ylim(-10, B+10); ax1.set_aspect('equal')
    st.pyplot(fig1)

with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(); ax2 = fig2.add_subplot(111, projection='3d')
    
    # Basis steen (Spook)
    z = np.array([[0,0,0], [L,0,0], [L,B,0], [0,B,0], [0,0,H], [L,0,H], [L,B,H], [0,B,H]])
    v = [[z[0],z[1],z[2],z[3]], [z[4],z[5],z[6],z[7]], [z[0],z[1],z[5],z[4]], [z[1],z[2],z[6],z[5]], [z[2],z[3],z[7],z[6]], [z[3],z[0],z[4],z[7]]]
    ax2.add_collection3d(Poly3DCollection(v, facecolors='gray', alpha=0.05, edgecolors='black', linestyles=':'))

    # Specifieke 3D objecten
    if prod_3d:
        ax2.add_collection3d(Poly3DCollection(prod_3d, facecolors='cyan', alpha=0.7, edgecolors='blue'))
    
    # Visualisatie van Sparren/Zool (horizontale zaagsnede)
    if type_trans in ["Sparren", "Zool"]:
        z_level = H - dikte if type_trans == "Zool" else H/2
        v_zaag = [[0,0,z_level], [L,0,z_level], [L,B,z_level], [0,B,z_level]]
        ax2.add_collection3d(Poly3DCollection([v_zaag], facecolors='red', alpha=0.5))

    ax2.set_xlim(0, L); ax2.set_ylim(0, B); ax2.set_zlim(0, H)
    st.pyplot(fig2)
