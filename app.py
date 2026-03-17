import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="Maten Tool Pro", layout="wide")
st.title("📏 Universele Maten Tool")

# 1. Kies het type vorm
vorm_type = st.sidebar.selectbox("Kies een vorm", ["Rechthoek / Balk", "L-Vorm"])

st.sidebar.divider()

# 2. Input op basis van keuze
if vorm_type == "Rechthoek / Balk":
    l1 = st.sidebar.number_input("Lengte (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Breedte (cm)", min_value=1.0, value=50.0)
    h = st.sidebar.number_input("Hoogte (cm)", min_value=0.1, value=40.0)
    dikte = 0.0 # Niet van toepassing bij balk
    grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    oppervlakte = l1 * l2
else:
    l1 = st.sidebar.number_input("Lengte Zijde 1 (cm)", min_value=1.0, value=100.0)
    l2 = st.sidebar.number_input("Lengte Zijde 2 (cm)", min_value=1.0, value=60.0)
    dikte = st.sidebar.number_input("Dikte (cm)", min_value=0.1, max_value=float(
