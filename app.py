import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from kerykeion import KrInstance
from plotly.subplots import make_subplots

# --- 設定: 4元素と星座の対応 ---
ELEMENTS = {
    "Fire": ["Ari", "Leo", "Sag"],  # 火
    "Earth": ["Tau", "Vir", "Cap"], # 地
    "Air": ["Gem", "Lib", "Aqr"],   # 風
    "Water": ["Can", "Sco", "Pis"]  # 水
}

ELEMENT_JP = {
    "Fire": "火 (直感/情熱)",
    "Earth": "地 (感覚/現実)",
    "Air": "風 (思考/情報)",
    "Water": "水 (感情/共感)"
}

# --- 天体のスコア配分 ---
PLANET_SCORES = {
    "Sun": 5, "Moon": 5, "Asc": 5, "Mc": 5,    # 個人への影響大
    "Mercury": 3, "Venus": 3, "Mars": 3,       # 次に強い
    "Jupiter": 2, "Saturn": 2,                 # 社会天体
    "Uranus": 1, "Neptune": 1, "Pluto": 1      # 世代天体
}

def get_element(sign_abbr):
    """星座名からエレメント（火地風水）を判定"""
    for element, signs in ELEMENTS.items():
        if sign_abbr in signs:
            return element
    return None

def main():
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")
    
    st.title("Aroma Soul Navigation 🌟")
    st.markdown("### 星（先天的な資質）と 香り（現在の状態）のバランス分析")

    # --- サイドバー: 入力エリア ---
    with st.sidebar:
        st.header("1. 出生データの入力")
        name = st.text_input("お名前", "Guest")
        b_year = st.number_input("年", 1950, 2025, 1990)
        b_month = st.number_input("月", 1, 12, 1)
        b_day = st.number_input("日", 1, 31, 1)
        b
