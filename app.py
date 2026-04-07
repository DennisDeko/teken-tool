import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ----------------------------
# Helpers
# ----------------------------
def clamp(val, low, high):
    return max(low, min(high, val))

def parse_float(val, default):
    try:
        return float(val)
    except Exception:
        return float(default)

def cuboid_faces(L, B, H):
    # 8 vertices
    v = np.array([
        [0, 0, 0],
        [L, 0, 0],
        [L, B, 0],
        [0, B, 0],
        [0, 0, H],
        [L, 0, H],
        [L, B, H],
        [0, B, H]
    ], dtype=float)

    faces = [
        [v[0], v[1], v[2], v[3]],  # bottom
        [v[4], v[5], v[6], v[7]],  # top
        [v[0], v[1], v[5], v[4]],  # y=0 face
        [v[3], v[2], v[6], v[7]],  # y=B face
        [v[0], v[3], v[7], v[4]],  # x=0 face
        [v[1], v[2], v[6], v[5]]   # x=L face
    ]
    return faces

def draw_plan_2d(L, B, strip_t, side, kerf):
    # Top view: x = length, y = width
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.set_title("Bovenaanzicht (L x B) met strip-zaaglijn(en)")
    ax.set_aspect("equal", adjustable="box")

    # Outline of stone
    ax.plot([0, L, L, 0, 0], [0, 0, B, B, 0], linewidth=2)

    # Determine saw lines in y-direction (parallel to x-axis)
    # We draw the cut line position(s) inside [0,B]
    # Strip thickness is measured from the chosen side.
    lines_y = []
    if side in ["Links", "Beide"]:
        lines_y.append(strip_t)
    if side in ["Rechts", "Beide"]:
        lines_y.append(B - strip_t)

    # Draw saw lines + kerf band
    for y in lines_y:
        y = clamp(y, 0, B)
        ax.hlines(y, xmin=0, xmax=L, colors="crimson", linewidth=2)
        if kerf > 0:
            y0 = y - kerf / 2.0
            y1 = y + kerf / 2.0
            y0 = clamp(y0, 0, B)
            y1 = clamp(y1, 0, B)
            ax.fill_between([0, L], [y0, y0], [y1, y1], color="crimson", alpha=0.15)

        ax.text(L * 0.01, y + (B * 0.02), "Zaaglijn @ y=" + str(round(y, 1)) + "mm", color="crimson", fontsize=9)

    # Annotate dimensions
    ax.text(L/2, -B*0.08, "L = " + str(round(L, 1)) + " mm", ha="center", va="top")
    ax.text(-L*0.01, B/2, "B = " + str(round(B, 1)) + " mm", rotation=90, ha="right", va="center")

    # Show strip spec
    ax.text(L * 0.5, B * 1.08,
            "Strip dikte = " + str(round(strip_t, 1)) + " mm | Zijde = " + side + " | Zaagdik/kerf = " + str(round(kerf, 1)) + " mm",
            ha="center")

    ax.set_xlim(-L*0.02, L*1.02)
    ax.set_ylim(-B*0.15, B*1.15)
    ax.axis("off")
    st.pyplot(fig)

def draw_preview_3d(L, B, H, strip_t, side, kerf):
    # Simple 3D preview: draw brick + semi-transparent strip region(s)
    fig = plt.figure(figsize=(8.5, 5.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("3D preview (indicatief)")

    faces = cuboid_faces(L, B, H)
    poly = Poly3DCollection(faces, facecolor=(0.85, 0.85, 0.85, 0.35), edgecolor=(0.2, 0.2, 0.2, 0.6), linewidths=0.8)
    ax.add_collection3d(poly)

    # Strip regions: volume removed depends on side(s)
    # We visualize the strip as a colored slab from y in [0,strip_t] or [B-strip_t,B]
    slabs = []
    if side in ["Links", "Beide"]:
        slabs.append((0.0, strip_t))
    if side in ["Rechts", "Beide"]:
        slabs.append((B-strip_t, B))

    for (y0, y1) in slabs:
        y0 = clamp(y0, 0, B)
        y1 = clamp(y1, 0, B)
        # slab cuboid vertices
        v = np.array([
            [0, y0, 0],
            [L, y0, 0],
            [L, y1, 0],
            [0, y1, 0],
            [0, y0, H],
            [L, y0, H],
            [L, y1, H],
            [0, y1, H]
        ], dtype=float)

        slab_faces = [
            [v[0], v[1], v[2], v[3]],
            [v[4], v[5], v[6], v[7]],
            [v[0], v[1], v[5], v[4]],
            [v[3], v[2], v[6], v[7]],
            [v[0], v[3], v[7], v[4]],
            [v[1], v[2], v[6], v[5]]
        ]
        slab_poly = Poly3DCollection(slab_faces, facecolor=(0.86, 0.1, 0.1, 0.18), edgecolor=(0.86, 0.1, 0.1, 0.35), linewidths=0.6)
        ax.add_collection3d(slab_poly)

    # Kerf hint: draw line(s) at the cut plane(s)
    lines_y = []
    if side in ["Links", "Beide"]:
        lines_y.append(strip_t)
    if side in ["Rechts", "Beide"]:
        lines_y.append(B - strip_t)

    for y in lines_y:
        y = clamp(y, 0, B)
        ax.plot([0, L], [y, y], [0, 0], color="crimson", linewidth=2)

    ax.set_xlim(0, L)
    ax.set_ylim(0, B)
    ax.set_zlim(0, H)

    ax.set_xlabel("L (mm)")
    ax.set_ylabel("B (mm)")
    ax.set_zlabel("H (mm)")

    # View angle
    ax.view_init(elev=20, azim=-55)

    st.pyplot(fig)

# ----------------------------
# UI
# ----------------------------
st.title("DEKO Strip-zaag tool (lange kant)")

with st.sidebar:
    st.header("1) Basismaat steen")

    preset = st.selectbox(
        "Kies standaard maat",
        ["Vrij invoeren", "Waalformaat (210x100x50)", "Dikformaat (210x100x65)"]
    )

    if preset == "Waalformaat (210x100x50)":
        L0, B0, H0 = 210.0, 100.0, 50.0
    elif preset == "Dikformaat (210x100x65)":
        L0, B0, H0 = 210.0, 100.0, 65.0
    else:
        L0, B0, H0 = 210.0, 100.0, 50.0

    L = st.number_input("Lengte L (mm)", min_value=1.0, value=float(L0), step=1.0)
    B = st.number_input("Breedte B (mm)", min_value=1.0, value=float(B0), step=1.0)
    H = st.number_input("Hoogte H (mm)", min_value=1.0, value=float(H0), step=1.0)

    st.header("2) Strip zagen vanaf lange kant")
    strip_t = st.number_input("Strip dikte (mm) vanaf zijkant", min_value=0.0, value=23.0, step=0.5)

    side = st.radio("Welke zijde", ["Links", "Rechts", "Beide"], index=0)

    st.header("3) Zaag instellingen")
    kerf = st.number_input("Zaagblad dikte / kerf (mm)", min_value=0.0, value=3.0, step=0.5)

    st.header("4) Weergave")
    show_3d = st.toggle("Toon 3D preview", value=False)

# ----------------------------
# Validatie + afgeleide resultaten
# ----------------------------
warnings = []
strip_t_eff = strip_t

if strip_t_eff <= 0:
    warnings.append("Strip dikte is 0 of kleiner. Er wordt niets gezaagd.")

if strip_t_eff >= B and side != "Beide":
    warnings.append("Strip dikte is groter of gelijk aan B. Dat is geen 'strip' meer.")
if strip_t_eff * 2 >= B and side == "Beide":
    warnings.append("Bij 'Beide' is 2x strip dikte groter of gelijk aan B: strips overlappen of nemen alles weg.")

# Compute outputs (strip width removed etc.)
rows = []
if side in ["Links", "Beide"]:
    rows.append({"Zijde": "Links", "Strip dikte (mm)": strip_t_eff, "Zaaglijn y (mm vanaf links)": strip_t_eff})
if side in ["Rechts", "Beide"]:
    rows.append({"Zijde": "Rechts", "Strip dikte (mm)": strip_t_eff, "Zaaglijn y (mm vanaf links)": B - strip_t_eff})

out_df = pd.DataFrame(rows)

# ----------------------------
# Main layout
# ----------------------------
col_a, col_b = st.columns([1.15, 0.85])

with col_a:
    st.subheader("Tekening")
    draw_plan_2d(L=L, B=B, strip_t=strip_t_eff, side=side, kerf=kerf)
    if show_3d:
        draw_preview_3d(L=L, B=B, H=H, strip_t=strip_t_eff, side=side, kerf=kerf)

with col_b:
    st.subheader("Samenvatting")
    st.write("Steen: **" + str(round(L, 1)) + " x " + str(round(B, 1)) + " x " + str(round(H, 1)) + " mm**")
    st.write("Strip: **" + str(round(strip_t_eff, 1)) + " mm** vanaf: **" + side + "**")
    st.write("Kerf: **" + str(round(kerf, 1)) + " mm**")

    if len(warnings) > 0:
        st.warning("Let op:\n\n- " + "\n- ".join(warnings))
    else:
        st.success("OK. Dit is een nette strip-snede setup.")

    st.subheader("Zaaglijnen (intern)")
    if len(out_df) == 0:
        st.info("Geen zaaglijnen (strip dikte is 0 of er is niets gekozen).")
    else:
        st.dataframe(out_df, use_container_width=True, hide_index=True)

    csv_bytes = out_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv_bytes,
        file_name="strip_zaaglijnen.csv",
        mime="text/csv",
        use_container_width=True
    )

st.caption("Definitie in deze tool: strip dikte = afstand vanaf lange zijkant over de breedte (B).")
