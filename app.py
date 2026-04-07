import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ----------------------------
# Helpers
# ----------------------------

def clamp(val, low, high):
    return max(low, min(high, val))

# ----------------------------
# Tekenen
# ----------------------------

def draw_plan_2d(L, B, strip_t, side, kerf):
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.set_title("Bovenaanzicht (L × B)")
    ax.set_aspect("equal")

    # Buitencontour steen
    ax.add_patch(plt.Rectangle((0, 0), L, B, fill=False))

    # Zaaglijnen
    if side in ["Links", "Beide"]:
        y = strip_t
        ax.axhline(y, color="red", lw=2, label="Zaaglijn links")
        ax.axhline(y + kerf, color="red", lw=1, linestyle="--")

    if side in ["Rechts", "Beide"]:
        y = B - strip_t
        ax.axhline(y, color="blue", lw=2, label="Zaaglijn rechts")
        ax.axhline(y - kerf, color="blue", lw=1, linestyle="--")

    ax.set_xlim(0, L)
    ax.set_ylim(0, B)
    ax.set_xlabel("Lengte (mm)")
    ax.set_ylabel("Breedte (mm)")
    ax.legend()
    st.pyplot(fig)


def draw_preview_3d(L, B, H, strip_t, side):
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("3D preview (indicatief)")

    # Cuboid vertices
    x = [0, L]
    y = [0, B]
    z = [0, H]

    verts = [
        [(x[0], y[0], z[0]), (x[1], y[0], z[0]), (x[1], y[1], z[0]), (x[0], y[1], z[0])],
        [(x[0], y[0], z[1]), (x[1], y[0], z[1]), (x[1], y[1], z[1]), (x[0], y[1], z[1])]
    ]

    ax.add_collection3d(
        Poly3DCollection(verts, facecolors="lightgrey", alpha=0.4)
    )

    ax.set_xlim(0, L)
    ax.set_ylim(0, B)
    ax.set_zlim(0, H)
    ax.set_xlabel("L")
    ax.set_ylabel("B")
    ax.set_zlabel("H")

    st.pyplot(fig)

# ----------------------------
# UI
# ----------------------------

st.title("DEKO Strip‑zaag tool (lange kant)")

with st.sidebar:
    st.header("Basismaat steen")
    L = st.number_input("Lengte L (mm)", 100.0, 2000.0, 600.0)
    B = st.number_input("Breedte B (mm)", 50.0, 600.0, 200.0)
    H = st.number_input("Hoogte H (mm)", 20.0, 200.0, 60.0)

    st.header("Strip")
    strip_t = st.number_input("Strip dikte (mm)", 0.0, B, 20.0)
    kerf = st.number_input("Zaagbreedte / kerf (mm)", 0.0, 10.0, 3.0)
    side = st.selectbox("Zijde", ["Links", "Rechts", "Beide"])

    show_3d = st.checkbox("Toon 3D preview")

# ----------------------------
# Validatie
# ----------------------------

warnings = []

if strip_t <= 0:
    warnings.append("Stripdikte is 0 → er wordt niets gezaagd.")

if side == "Beide" and strip_t * 2 >= B:
    warnings.append("Strips overlappen of nemen de volledige breedte weg.")

for w in warnings:
    st.warning(w)

# ----------------------------
# Layout
# ----------------------------

col_a, col_b = st.columns([1.2, 0.8])

with col_a:
    st.subheader("Tekening")
    draw_plan_2d(L, B, strip_t, side, kerf)
    if show_3d:
        draw_preview_3d(L, B, H, strip_t, side)

with col_b:
    st.subheader("Samenvatting")
    st.write(f"**Steen:** {L:.1f} × {B:.1f} × {H:.1f} mm")
    st.write(f"**Strip:** {strip_t:.1f} mm — zijde: **{side}**")
    st.write(f"**Kerf:** {kerf:.1f} mm")
    st.caption("Stripdikte = afstand gemeten over de breedte (B)")
