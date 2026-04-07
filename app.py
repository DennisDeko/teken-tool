import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Config
# ----------------------------
st.set_page_config(page_title="DEKO Maatwerk Tool", layout="wide")

# ----------------------------
# Standaard steenmaten (L, B, H) in mm
# ----------------------------
STEEN_MATEN = {
    "Vrij invoeren": (210.0, 100.0, 50.0),
    "Waalformaat": (210.0, 100.0, 50.0),
    "Dikformaat / waaldikformaat": (210.0, 100.0, 65.0),
    "Brabantse steen": (180.0, 88.0, 53.0),
    "Deens formaat": (228.0, 108.0, 54.0),
    "Engels formaat": (210.0, 102.5, 65.0),
    "Normalformat (NF)": (240.0, 115.0, 71.0),
}

# ----------------------------
# Helpers
# ----------------------------
def parse_mm_list(mm_text: str) -> list:
    cleaned = (mm_text or "").strip()
    if cleaned == "":
        return []
    cleaned = cleaned.replace(";", ",").replace("\n", ",")
    parts = [p.strip() for p in cleaned.split(",") if p.strip() != ""]
    mm_vals = []
    for p in parts:
        try:
            mm_vals.append(float(p.replace("mm", "").strip()))
        except Exception:
            pass
    return mm_vals

def normalize_positions(mm_vals: list, L: float, side: str) -> list:
    # Convert to positions measured from LEFT
    # side: "Links" or "Rechts"
    pos = []
    for v in mm_vals:
        if side == "Links":
            x = v
        else:
            x = L - v
        pos.append(x)
    return pos

def sanitize_positions(pos: list, L: float, margin: float = 0.0) -> list:
    # Keep only within [margin, L - margin]
    out = []
    for x in pos:
        if x is None:
            continue
        if x >= margin and x <= (L - margin):
            out.append(float(x))
    # Remove duplicates (within small tolerance)
    out_sorted = sorted(out)
    merged = []
    tol = 0.0001
    for x in out_sorted:
        if len(merged) == 0:
            merged.append(x)
        else:
            if abs(x - merged[-1]) > tol:
                merged.append(x)
    return merged

def compute_segments_from_cuts(L: float, cut_positions_left: list, kerf: float) -> pd.DataFrame:
    # Interpret cuts as full-through cuts at positions x (from left).
    # If kerf > 0, you lose kerf at each cut (simple model).
    cuts = sorted(cut_positions_left)
    # Boundary positions include ends
    boundaries = [0.0] + cuts + [L]
    segs = []
    for i in range(len(boundaries) - 1):
        a = boundaries[i]
        b = boundaries[i + 1]
        raw_len = b - a
        loss = 0.0
        # each internal segment touches a cut at most one side,
        # but a simple and understandable UX model is:
        # subtract kerf once per cut, applied between segments
        if i > 0:
            loss += kerf / 2.0
        if i < len(boundaries) - 2:
            loss += kerf / 2.0
        eff_len = max(raw_len - loss, 0.0)
        segs.append({"segment": i + 1, "start_mm": a, "end_mm": b, "raw_len_mm": raw_len, "eff_len_mm": eff_len})
    return pd.DataFrame(segs)

def plot_top_view(L: float, B: float, cuts_left: list, label_rows: list):
    fig = plt.figure(figsize=(10, 2.8))
    ax = fig.add_subplot(111)

    # Outline
    ax.plot([0, L, L, 0, 0], [0, 0, B, B, 0], linewidth=2)

    # Cuts
    for idx, x in enumerate(cuts_left):
        ax.plot([x, x], [0, B], linestyle="--", linewidth=2)
        if idx < len(label_rows):
            ax.text(x, B + (B * 0.06), label_rows[idx], ha="center", va="bottom", fontsize=9, rotation=0)

    ax.set_xlim(-L * 0.05, L * 1.05)
    ax.set_ylim(-B * 0.2, B * 1.35)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Bovenaanzicht (L x B) met X-snedes")
    ax.set_xlabel("Lengte (mm)")
    ax.set_ylabel("Breedte (mm)")
    ax.grid(True, alpha=0.2)
    return fig

# ----------------------------
# UI
# ----------------------------
st.title("DEKO Maatwerk Tool")
st.caption("Focus: snel en foutarm X-snedes invoeren, inclusief snedes vanaf de andere kant.")

col_a, col_b = st.columns([1.1, 1.9])

with col_a:
    st.subheader("1) Steenformaat")
    keuze = st.selectbox("Kies standaard maat", list(STEEN_MATEN.keys()), index=1)
    std_L, std_B, std_H = STEEN_MATEN[keuze]

    use_free = (keuze == "Vrij invoeren")
    if use_free:
        L = st.number_input("Lengte L (mm)", min_value=1.0, value=float(std_L), step=1.0)
        B = st.number_input("Breedte B (mm)", min_value=1.0, value=float(std_B), step=1.0)
        H = st.number_input("Hoogte H (mm)", min_value=1.0, value=float(std_H), step=1.0)
    else:
        L = float(std_L)
        B = float(std_B)
        H = float(std_H)
        st.write("Gekozen maat (mm)")
        st.code("L = " + str(L) + "\nB = " + str(B) + "\nH = " + str(H))

    st.subheader("2) Zaaginstellingen")
    kerf = st.number_input("Zaagbreedte / kerf (mm)", min_value=0.0, value=3.0, step=0.5)
    st.caption("Kerf wordt simpel verdeeld over aangrenzende segmenten (½ kerf per zijde).")

with col_b:
    st.subheader("3) X-snedes invoeren (gebruiksvriendelijk)")

    st.markdown("**Set 1** (bijv. X1 snedes)  ")
    side1 = st.selectbox("Referentiekant set 1", ["Links", "Rechts"], index=0, help="Links = vanaf linkerkop. Rechts = vanaf rechterkop.")
    x1_text = st.text_input("Afstanden (mm), komma-gescheiden", value="23", help="Voorbeeld: 23, 40, 55")

    st.markdown("**Set 2** (altijd vanaf de andere kant)  ")
    # Auto default: opposite side of side1
    default_side2 = "Rechts" if side1 == "Links" else "Links"
    side2 = st.selectbox("Referentiekant set 2", ["Links", "Rechts"], index=0 if default_side2 == "Links" else 1)
    x2_text = st.text_input("Afstanden (mm), komma-gescheiden", value="", help="Bijv. 23 betekent 23 mm vanaf de andere kopzijde.")

    st.markdown("**Opties**")
    dedup = st.checkbox("Dubbele snedes samenvoegen", value=True)
    hide_outside = st.checkbox("Snedes buiten bereik automatisch negeren", value=True)

# ----------------------------
# Compute
# ----------------------------
x1_vals = parse_mm_list(x1_text)
x2_vals = parse_mm_list(x2_text)

cuts1_left = normalize_positions(x1_vals, L, side1)
cuts2_left = normalize_positions(x2_vals, L, side2)

all_cuts_left_raw = cuts1_left + cuts2_left

margin = 0.0
if hide_outside:
    all_cuts_left = sanitize_positions(all_cuts_left_raw, L, margin=margin)
else:
    # keep, but still sort
    all_cuts_left = sorted([float(x) for x in all_cuts_left_raw])

if dedup:
    all_cuts_left = sanitize_positions(all_cuts_left, L, margin=margin)

# Labels for drawing: show original intent (L/R + distance)
labels = []
for v in x1_vals:
    labels.append("S1 " + side1[0] + " " + str(v))
for v in x2_vals:
    labels.append("S2 " + side2[0] + " " + str(v))

# But after sanitizing/dedup, labels may not match 1:1.
# For UX, we just label in order; the table below is the truth.
label_rows = []
for i, x in enumerate(all_cuts_left):
    label_rows.append("X" + str(i + 1) + " @ " + str(round(x, 2)))

# ----------------------------
# Output
# ----------------------------
st.divider()
out_left, out_right = st.columns([1.3, 1.0])

with out_left:
    st.subheader("Resultaat: tekening")
    fig = plot_top_view(L, B, all_cuts_left, label_rows)
    st.pyplot(fig, clear_figure=True)

    st.caption("Alle posities in de tabel hieronder zijn omgerekend naar 'vanaf links' zodat alles consistent is.")

with out_right:
    st.subheader("Resultaat: tabel")
    cuts_df = pd.DataFrame({"cut_index": list(range(1, len(all_cuts_left) + 1)), "x_from_left_mm": all_cuts_left})
    if len(cuts_df) == 0:
        st.info("Geen geldige snedes ingevoerd.")
    else:
        st.dataframe(cuts_df, use_container_width=True, hide_index=True)

    seg_df = compute_segments_from_cuts(L, all_cuts_left, kerf)
    st.subheader("Segmenten (na snedes)")
    st.dataframe(seg_df, use_container_width=True, hide_index=True)

    csv_bytes = seg_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download segmenten CSV",
        data=csv_bytes,
        file_name="segmenten.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()

# ----------------------------
# UX warnings
# ----------------------------
warnings = []
for v in x1_vals:
    if v < 0:
        warnings.append("Set 1 bevat negatieve afstand: " + str(v))
    if v > L:
        warnings.append("Set 1 afstand groter dan lengte L: " + str(v) + " > " + str(L))

for v in x2_vals:
    if v < 0:
        warnings.append("Set 2 bevat negatieve afstand: " + str(v))
    if v > L:
        warnings.append("Set 2 afstand groter dan lengte L: " + str(v) + " > " + str(L))

if len(all_cuts_left) > 0:
    if min(all_cuts_left) <= 0.0 or max(all_cuts_left) >= L:
        warnings.append("Er zit een snede op/tegen de rand (0 of L). Meestal wil je een snede binnen de steen.")

# Show warnings
if len(warnings) > 0:
    st.warning("Controleer even:\n- " + "\n- ".join(warnings))
else:
    st.success("Inputs zien er logisch uit.")

st.caption("Tip: Wil je dat Set 2 écht altijd automatisch 'andere kant' is zonder dropdown? Dan kan ik die selectbox weghalen en vastzetten.")
