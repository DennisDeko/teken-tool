import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="DEKO Zaag Tool - Strippen & Koppen", layout="wide")

# --- DATABASE ---
steen_maten = {
    "Waalformaat": (210, 100, 50),
    "Dikformaat": (210, 100, 65),
    "Vechtformaat": (210, 100, 40),
    "Vrij invoeren": (210, 100, 50)
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Steenkeuze")
    keuze = st.selectbox("Formaat", list(steen_maten.keys()))
    std_l, std_b, std_h = steen_maten[keuze]
    
    L = st.number_input("Lengte (L)", value=float(std_l))
    B = st.number_input("Breedte (B)", value=float(std_b))
    H = st.number_input("Hoogte (H)", value=float(std_h))

    st.header("2. Bewerking")
    type_trans = st.radio("Type", ["Strippen (Langs)", "Koppen (Kort)"])
    aantal = st.radio("Aantal", ["1-zijdig", "2-zijdig"])
    
    dikte = st.number_input("Dikte strip/kop (mm)", value=23.0)
    zaagblad = st.slider("Zaagblad dikte (mm)", 0.0, 5.0, 3.0)

# --- CALCULATIE ---
zaaglijnen = [] # Formaat: (x, y, breedte, hoogte)

if type_trans == "Strippen (Langs)":
    # Zaaglijnen parallel aan de Lange zijde (over de breedte B)
    zaaglijnen.append((0, dikte, L, zaagblad))
    if aantal == "2-zijdig":
        zaaglijnen.append((0, B - dikte - zaagblad, L, zaagblad))
else:
    # Zaaglijnen parallel aan de Korte zijde (over de lengte L)
    zaaglijnen.append((dikte, 0, zaagblad, B))
    if aantal == "2-zijdig":
        zaaglijnen.append((L - dikte - zaagblad, 0, zaagblad, B))

# --- VISUALISATIE ---
st.subheader(f"Zaagplan: {type_trans} ({aantal})")

fig, ax = plt.subplots(figsize=(8, 4))

# De basissteen
ax.add_patch(plt.Rectangle((0, 0), L, B, facecolor='lightgray', alpha=0.3, edgecolor='black', lw=2))

# De zaaglijnen
for (x, y, w, h) in zaaglijnen:
    ax.add_patch(plt.Rectangle((x, y), w, h, color='red', alpha=0.8))
    
    # Maatvoering tekst
    if type_trans == "Strippen (Langs)":
        ax.text(L/2, y + h/2, f"Zaag op {y}mm", color='red', fontweight='bold', ha='center', va='center', backgroundcolor='white')
    else:
        ax.text(x + w/2, B/2, f"{x}mm", color='red', fontweight='bold', rotation=90, ha='center', va='center', backgroundcolor='white')

# Instellingen voor de plot
ax.set_xlim(-20, L + 20)
ax.set_ylim(-20, B + 20)
ax.set_aspect('equal')
ax.axis('off')

st.pyplot(fig)

# --- TABEL ---
st.divider()
st.table({
    "Omschrijving": ["Steenmaat", "Bewerking", "Strip/Kop dikte", "Zaagblad"],
    "Waarde": [f"{L}x{B}x{H} mm", f"{type_trans} ({aantal})", f"{dikte} mm", f"{zaagblad} mm"]
})
