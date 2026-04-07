import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dataclasses import dataclass
from typing import List, Tuple, Optional


# ----------------------------
# App config
# ----------------------------
st.set_page_config(page_title="DEKO Maatwerk Tool", layout="wide")


# ----------------------------
# Data: standaard steenmaten
# (je kunt deze lijst uitbreiden/opschonen)
# ----------------------------
STEEN_MATEN = {
    "Vrij invoeren": (210.0, 100.0, 50.0),
    "Waalformaat": (210.0, 100.0, 50.0),
    "Dikformaat / waaldikformaat": (210.0, 100.0, 65.0),
    "Brabantse steen": (180.0, 88.0, 53.0),
    "Deens formaat": (228.0, 108.0, 54.0),
    "Dordtse steen": (180.0, 88.0, 43.0),
    "Dubbel waalformaat": (210.0, 100.0, 110.0),
    "Dunnformat (DF)": (240.0, 115.0, 52.0),
    "Engels formaat": (210.0, 102.5, 65.0),
    "Euroformat": (188.0, 90.0, 88.0),
    "F52": (230.0, 110.0, 57.0),
    "Friese drieling": (184.0, 80.0, 40.0),
    "Friese mop": (217.0, 103.0, 45.0),
    "Goudse steen": (155.0, 72.0, 53.0),
    "Groninger steen": (240.0, 120.0, 60.0),
    "Hilversums formaat": (240.0, 90.0, 40.0),
    "IJsselformaat": (160.0, 78.0, 41.0),
    "Juffertje": (175.0, 82.0, 40.0),
    "Kathedraal I": (240.0, 115.0, 65.0),
    "Kathedraal II": (270.0, 105.0, 55.0),
    "Kloostermop I": (280.0, 105.0, 80.0),
    "Kloostermop II": (320.0, 130.0, 80.0),
    "Moduul 190-90-50": (190.0, 90.0, 50.0),
    "Moduul 190-90-90": (190.0, 90.0, 90.0),
    "Moduul 240-90-90": (240.0, 90.0, 90.0),
    "Moduul 290-115-190": (290.0, 115.0, 190.0),
    "Moduul 290-115-90": (290.0, 115.0, 90.0),
    "Moduul 290-90-190": (290.0, 90.0, 190.0),
    "Moduul 290-90-90": (290.0, 90.0, 90.0),
    "Normalformat (NF)": (240.0, 115.0, 71.0),
    "Oldenburgerformat (OF)": (210.0, 105.0, 52.0),
    "Reichsformat (RF)": (240.0, 115.0, 61.0),
    "Rijnformaat": (180.0, 87.0, 41.0),
    "Romeins formaat": (240.0, 115.0, 42.0),
    "Utrechts plat": (215.0, 102.0, 38.0),
    "Vechtformaat": (210.0, 100.0, 40.0),
    "Verblender (2DF)": (240.0, 115.0, 113.0),
}


# ----------------------------
# Modellen / helpers
# ----------------------------
@dataclass
class Brick:
    L: float  # lengte
    B: float  # breedte
    H: float  # hoogte


@dataclass
class CutPlan:
    # zaagsneden in mm vanaf referentie (0 = linkerkant / onderkant)
    # Voor gebruiksgemak houden we het simpel: rechte sneden op 1 as.
    axis: str  # "L", "B", "H"
    positions_mm: List[float]
    kerf_mm: float  # zaagblad dikte
    keep_side: str  # "links/onder" of "rechts/boven" -> voor interpretatie/tekst
    label: str


def clamp_sorted_unique(vals: List[float], lo: float, hi: float) -> List[float]:
    cleaned = []
    for v in vals:
        if v is None:
            continue
        if np.isnan(v):
            continue
        if v < lo or v > hi:
            continue
        cleaned.append(float(v))
    cleaned = sorted(set([round(v, 3) for v in cleaned]))
    return cleaned


def parse_mm_list(text: str) -> List[float]:
    # accepteert: "10, 20, 30" of "10 20 30" of "10;20;30"
    if text is None:
        return []
    t = text.strip()
    if t == "":
        return []
    for sep in [";", "\n", "\t", " "]:
        t = t.replace(sep, ",")
    parts = [p.strip() for p in t.split(",") if p.strip() != ""]
    out = []
    for p in parts:
        try:
            out.append(float(p.replace(",", ".")))
        except Exception:
            # niet parsebaar -> overslaan
            pass
    return out


def segments_from_cuts(total: float, cut_positions: List[float], kerf: float) -> List[Tuple[float, float]]:
    """
    Return segments as (start, end) in mm along an axis.
    We tekenen snedes als lijnen; segmenten zijn handig voor maat-samenvatting.
    Vereenvoudigde aanname: kerf beïnvloedt niet segment-lengtes in de tekening,
    maar we rapporteren wel hoeveel materiaal verdwijnt.
    """
    cuts = [c for c in cut_positions if 0.0 < c < total]
    cuts = sorted(cuts)
    pts = [0.0] + cuts + [total]
    segs = []
    for i in range(len(pts) - 1):
        segs.append((pts[i], pts[i + 1]))
    return segs


def draw_2d_view(ax, axis_total: float, other_total: float, cut_positions: List[float], title: str, axis_name: str):
    # rechthoek
    ax.plot([0, axis_total, axis_total, 0, 0], [0, 0, other_total, other_total, 0], linewidth=2)
    # snedes
    for c in cut_positions:
        ax.plot([c, c], [0, other_total], linestyle="--", linewidth=2)
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-0.05 * axis_total, 1.05 * axis_total)
    ax.set_ylim(-0.05 * other_total, 1.05 * other_total)
    ax.set_xlabel(axis_name + " (mm)")
    ax.set_ylabel("mm")
    ax.grid(True, alpha=0.25)


def draw_3d_preview(brick: Brick, cut_plan: Optional[CutPlan]):
    # Eenvoudige 3D wireframe + snijvlakken als translucent vlakken
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")

    L = brick.L
    B = brick.B
    H = brick.H

    # 8 corners
    corners = np.array([
        [0, 0, 0],
        [L, 0, 0],
        [L, B, 0],
        [0, B, 0],
        [0, 0, H],
        [L, 0, H],
        [L, B, H],
        [0, B, H],
    ])

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    for e in edges:
        p1 = corners[e[0]]
        p2 = corners[e[1]]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], linewidth=2)

    # snijvlakken
    if cut_plan is not None:
        for c in cut_plan.positions_mm:
            if cut_plan.axis == "L":
                xs = [c, c, c, c]
                ys = [0, B, B, 0]
                zs = [0, 0, H, H]
            elif cut_plan.axis == "B":
                xs = [0, L, L, 0]
                ys = [c, c, c, c]
                zs = [0, 0, H, H]
            else:
                xs = [0, L, L, 0]
                ys = [0, 0, B, B]
                zs = [c, c, c, c]
            ax.plot_trisurf(xs, ys, zs, color="red", alpha=0.15, linewidth=0.0)

    ax.set_xlabel("L (mm)")
    ax.set_ylabel("B (mm)")
    ax.set_zlabel("H (mm)")
    ax.set_title("3D preview (indicatief)")
    ax.view_init(elev=18, azim=35)
    plt.tight_layout()
    return fig


def build_summary(brick: Brick, cut_plan: Optional[CutPlan]) -> pd.DataFrame:
    if cut_plan is None:
        return pd.DataFrame([{
            "Producttype": "Steen",
            "As": "-",
            "Snelkeuze": "-",
            "L (mm)": brick.L,
            "B (mm)": brick.B,
            "H (mm)": brick.H,
            "Zaagblad (mm)": np.,
            "Aantal sneden": 0,
            "Kerf totaal (mm)": 0.0,
            "Opmerking": "Geen zaagplan geselecteerd",
        }])

    total = getattr(brick, cut_plan.axis)
    segs = segments_from_cuts(total, cut_plan.positions_mm, cut_plan.kerf_mm)
    kerf_total = max(0, len([c for c in cut_plan.positions_mm if 0.0 < c < total])) * cut_plan.kerf_mm

    rows = []
    for i, (a, b) in enumerate(segs, start=1):
        rows.append({
            "Segment": i,
            "As": cut_plan.axis,
            "Start (mm)": a,
            "Eind (mm)": b,
            "Lengte (mm)": b - a
        })
    df_segs = pd.DataFrame(rows)

    meta = pd.DataFrame([{
        "Zaagplan": cut_plan.label,
        "As": cut_plan.axis,
        "Zaagblad (mm)": cut_plan.kerf_mm,
        "Aantal sneden": len([c for c in cut_plan.positions_mm if 0.0 < c < total]),
        "Kerf totaal (mm)": kerf_total,
        "Keep side": cut_plan.keep_side,
        "Steen L (mm)": brick.L,
        "Steen B (mm)": brick.B,
        "Steen H (mm)": brick.H,
    }])

    # combineer (voor export handig: meta boven, lege regel, segmenten)
    spacer = pd.DataFrame([{}])
    out = pd.concat([meta, spacer, df_segs], ignore_index=True)
    return out


# ----------------------------
# UI: header
# ----------------------------
col1, col2 = st.columns([1, 3])
with col1:
    # laat logo optioneel; als url faalt is het geen ramp
    try:
        st.image("https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg", width=180)
    except Exception:
        st.write("")
with col2:
    st.title("DEKO Maatwerk Editor")
    st.caption("Snel maten kiezen, zaagplan invullen, direct 2D/3D tekening + output voor productie.")


st.divider()


# ----------------------------
# Sidebar: stap-voor-stap
# ----------------------------
st.sidebar.header("Instellingen")

with st.sidebar.expander("1) Kies steenformaat", expanded=True):
    keuze_naam = st.selectbox("Snelkeuze formaat", list(STEEN_MATEN.keys()), index=1)
    std_L, std_B, std_H = STEEN_MATEN[keuze_naam]

    colA, colB, colC = st.columns(3)
    with colA:
        in_L = st.number_input("Lengte L (mm)", min_value=1.0, max_value=2000.0, value=float(std_L), step=1.0)
    with colB:
        in_B = st.number_input("Breedte B (mm)", min_value=1.0, max_value=2000.0, value=float(std_B), step=1.0)
    with colC:
        in_H = st.number_input("Hoogte H (mm)", min_value=1.0, max_value=2000.0, value=float(std_H), step=1.0)

brick_obj = Brick(L=float(in_L), B=float(in_B), H=float(in_H))

with st.sidebar.expander("2) Kies product en zaagplan", expanded=True):
    product_type = st.selectbox("Producttype", ["Steen (recht)", "Hoek (L-vorm)"], index=0)

    st.caption("Tip: kies eerst een template, dan pas fine-tunen.")
    if product_type.startswith("Steen"):
        template = st.selectbox(
            "Template",
            ["Geen (alleen maat tonen)", "1 snede (1 maat)", "2 sneden (3 segmenten)"],
            index=0
        )
    else:
        template = st.selectbox(
            "Template",
            ["Geen (alleen maat tonen)", "Hoek basis (indicatief)"],
            index=0
        )

with st.sidebar.expander("3) Zaag-invoer", expanded=True):
    # algemene kerf
    kerf_mm = st.number_input("Zaagblad dikte (kerf) mm", min_value=0.0, max_value=10.0, value=3.2, step=0.1)

    # as keuze: bij “Hoek” houden we ’t nog simpel (zelfde engine); je kunt later uitbreiden naar 2 assen
    axis_choice = st.selectbox("Zaag-as", ["L", "B", "H"], index=0)

    # defaults per template
    default_positions = ""
    if template == "1 snede (1 maat)":
        default_positions = str(round(getattr(brick_obj, axis_choice) / 2.0, 1))
    elif template == "2 sneden (3 segmenten)":
        total_val = getattr(brick_obj, axis_choice)
        default_positions = str(round(total_val / 3.0, 1)) + ", " + str(round(2.0 * total_val / 3.0, 1))
    elif template == "Hoek basis (indicatief)":
        total_val = getattr(brick_obj, axis_choice)
        default_positions = str(round(total_val / 2.0, 1))

    positions_text = st.text_input(
        "Zaagposities in mm vanaf 0 (komma-gescheiden)",
        value=default_positions,
        help="Voorbeeld: 35, 70, 120. Waardes buiten de steen worden genegeerd."
    )

    keep_side = st.radio("Welke kant is jouw referentie?", ["links/onder", "rechts/boven"], horizontal=True)

# maak cutplan (of None)
cut_plan_obj = None
raw_positions = parse_mm_list(positions_text)

axis_total = getattr(brick_obj, axis_choice)
clean_positions = clamp_sorted_unique(raw_positions, 0.0, axis_total)

if template == "Geen (alleen maat tonen)" or (positions_text.strip() == ""):
    cut_plan_obj = None
else:
    cut_plan_obj = CutPlan(
        axis=axis_choice,
        positions_mm=clean_positions,
        kerf_mm=float(kerf_mm),
        keep_side=keep_side,
        label=template
    )

# ----------------------------
# Validatie / UX feedback
# ----------------------------
issues = []
if cut_plan_obj is not None:
    if len(raw_positions) != len(clean_positions):
        issues.append("Sommige ingevoerde waardes zijn genegeerd (niet-numeriek of buiten bereik).")
    if any([p <= 0.0 or p >= axis_total for p in clean_positions]):
        issues.append("Zaagposities op 0 of exact op de rand zijn niet zinvol en worden genegeerd.")
    if len(clean_positions) == 0:
        issues.append("Geen geldige zaagposities over. Kies een andere template of vul posities in.")

if len(issues) > 0:
    for msg in issues:
        st.warning(msg)

# ----------------------------
# Main layout
# ----------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("Tekening")
    tab2d, tab3d = st.tabs(["2D (aanzichten)", "3D (preview)"])

    with tab2d:
        # 2D: toon relevante aanzichten + snedes op gekozen as
        fig = plt.figure(figsize=(12, 4))
        ax1 = fig.add_subplot(131)
        ax2 = fig.add_subplot(132)
        ax3 = fig.add_subplot(133)

        cuts = []
        if cut_plan_obj is not None:
            cuts = cut_plan_obj.positions_mm

        # Aanzicht 1: L x B (snedes op L)
        draw_2d_view(
            ax1,
            axis_total=brick_obj.L,
            other_total=brick_obj.B,
            cut_positions=cuts if axis_choice == "L" else [],
            title="Bovenaanzicht (L x B)",
            axis_name="L"
        )
        ax1.set_ylabel("B (mm)")

        # Aanzicht 2: L x H (snedes op L)
        draw_2d_view(
            ax2,
            axis_total=brick_obj.L,
            other_total=brick_obj.H,
            cut_positions=cuts if axis_choice == "L" else [],
            title="Zijaanzicht (L x H)",
            axis_name="L"
        )
        ax2.set_ylabel("H (mm)")

        # Aanzicht 3: B x H (snedes op B)
        draw_2d_view(
            ax3,
            axis_total=brick_obj.B,
            other_total=brick_obj.H,
            cut_positions=cuts if axis_choice == "B" else [],
            title="Vooraanzicht (B x H)",
            axis_name="B"
        )
        ax3.set_ylabel("H (mm)")

        plt.tight_layout()
        st.pyplot(fig)

        # Extra: als je op H snijdt, toon een aparte H view (simpel en duidelijk)
        if axis_choice == "H":
            fig2 = plt.figure(figsize=(8, 3.5))
            axh = fig2.add_subplot(111)
            draw_2d_view(
                axh,
                axis_total=brick_obj.H,
                other_total=brick_obj.L,
                cut_positions=cuts,
                title="Hoogte snedes (H x L) indicatief",
                axis_name="H"
            )
            axh.set_ylabel("L (mm)")
            plt.tight_layout()
            st.pyplot(fig2)

    with tab3d:
        fig3d = draw_3d_preview(brick_obj, cut_plan_obj)
        st.pyplot(fig3d)

with right:
    st.subheader("Output")
    st.caption("Dit is de checklist die je in werkplaats/tekening wil hebben.")

    st.write("**Gekozen formaat:** " + str(keuze_naam))
    st.write("**Steenmaat (mm):** L " + str(round(brick_obj.L, 2)) + " | B " + str(round(brick_obj.B, 2)) + " | H " + str(round(brick_obj.H, 2)))

    if cut_plan_obj is None:
        st.info("Geen zaagplan actief. Kies een template of vul zaagposities in.")
    else:
        st.write("**Zaag-as:** " + cut_plan_obj.axis)
        st.write("**Zaagposities (mm):** " + (", ".join([str(p) for p in cut_plan_obj.positions_mm]) if len(cut_plan_obj.positions_mm) > 0 else "-"))
        st.write("**Zaagblad (kerf) mm:** " + str(round(cut_plan_obj.kerf_mm, 2)))
        st.write("**Referentie:** " + cut_plan_obj.keep_side)

    st.divider()

    df_out = build_summary(brick_obj, cut_plan_obj)
    st.dataframe(df_out, use_container_width=True, height=320)

    # export
    csv_bytes = df_out.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download zaagplan CSV",
        data=csv_bytes,
        file_name="zaagplan.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()
st.caption("Volgende stap (als je wil): Hoek-product écht goed maken met 2 assen (L én B snedes) en vaste referentiehoeken + maatlijnen.")
