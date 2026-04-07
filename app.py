import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ----------------------------
# Tekenfunctie Hoek
# ----------------------------

def draw_hoek(A, B, D, E, strip, X=None):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Steenstrippen – Hoek")

    # ---- L-vorm steen ----
    # Lang been
    ax.add_patch(
        Rectangle((0, 0), A, B, facecolor="white", edgecolor="black", linewidth=1.5)
    )

    # Kort been
    ax.add_patch(
        Rectangle((0, B), D, E, facecolor="white", edgecolor="black", linewidth=1.5)
    )

    # ---- Strips ----
    # Strip lang been
    ax.add_patch(
        Rectangle((0, 0), strip, B, facecolor="#d9d9d9", edgecolor="black")
    )

    # Strip kort been
    ax.add_patch(
        Rectangle((0, B), strip, E, facecolor="#d9d9d9", edgecolor="black")
    )

    # ---- Labels ----
    ax.text(A * 0.6, B * 0.5, "Restant", color="gray", fontsize=9)

    # Maatletters
    ax.text(A / 2, -12, "A", ha="center", va="top", fontsize=10)
    ax.text(-12, B / 2, "B", ha="right", va="center", rotation=90, fontsize=10)

    ax.text(D / 2, B + E + 6, "D", ha="center", fontsize=10)
    ax.text(-12, B + E / 2, "E", ha="right", va="center", rotation=90, fontsize=10)

    # ---- Afkorten X (stippellijn) ----
    if X and X > 0 and X < A:
        ax.plot(
            [A - X, A - X],
            [0, B],
            linestyle="--",
            color="black"
        )
        ax.text(A - X + 3, B / 2, "X", fontsize=9)

    # ---- View limits ----
    ax.set_xlim(-30, A + 30)
    ax.set_ylim(-30, B + E + 30)

    return fig


# ----------------------------
# Streamlit UI
# ----------------------------

st.set_page_config(page_title="Steenstrippen – Hoek", layout="centered")
st.title("Steenstrippen – Hoek")

with st.sidebar:
    st.header("Afmetingen (mm)")

    A = st.number_input("A – lengte lang been", 100.0, 1200.0, 400.0, step=10.0)
    B = st.number_input("B – diepte lang been", 40.0, 400.0, 100.0, step=5.0)
    C = st.number_input("C – hoogte (alleen vermelden)", 20.0, 150.0, 60.0, step=5.0)
    D = st.number_input("D – lengte kort been", 40.0, 600.0, 200.0, step=10.0)
    E = st.number_input("E – diepte kort been", 30.0, 300.0, 80.0, step=5.0)

    strip = st.number_input("Stripdikte", 10.0, B, 30.0, step=5.0)
    X = st.number_input("Afkorten X (optioneel)", 0.0, A, 0.0, step=5.0)

st.subheader("Tekening")
fig = draw_hoek(A, B, D, E, strip, X if X > 0 else None)
st.pyplot(fig)

st.subheader("Samenvatting")
st.write(f"**A** = {A:.0f} mm")
st.write(f"**B** = {B:.0f} mm")
st.write(f"**C** = {C:.0f} mm (hoogte)")
st.write(f"**D** = {D:.0f} mm")
st.write(f"**E** = {E:.0f} mm")
st.write(f"**Strip** = {strip:.0f} mm")

if X > 0:
    st.write(f"**Afkorten X** = {X:.0f} mm")

st.caption(
    "Schematische tekening conform formulier ‘Steenstrippen Hoek’. "
    "Niet op schaal in hoogte (C)."
)
