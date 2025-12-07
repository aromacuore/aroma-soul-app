import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import flatlib
import os
import requests

# --- 🛠 辞書ファイル（エフェメリス）の自動ダウンロード ---
def download_ephemeris():
    files = {
        "sepl_18.se1": "https://raw.githubusercontent.com/astrorigin/pyswisseph/master/ephe/sepl_18.se1",
        "semo_18.se1": "https://raw.githubusercontent.com/astrorigin/pyswisseph/master/ephe/semo_18.se1"
    }
    
    for filename, url in files.items():
        if not os.path.exists(filename):
            try:
                with st.spinner(f'星のデータ({filename})をダウンロード中...（初回のみ）'):
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(filename, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                st.error(f"データのダウンロードに失敗しました: {e}")
                st.stop()

# ダウンロード実行とパス指定
download_ephemeris()
flatlib.setPath(os.getcwd())

# --- 🌟 47都道府県の座標データ (県庁所在地) ---
PREFECTURES = {
    "北海道": (43.06, 141.35), "青森県": (40.82, 140.74), "岩手県": (39.70, 141.15),
    "宮城県": (38.26, 140.87), "秋田県": (39.71, 140.10), "山形県": (38.24, 140.36),
    "福島県": (37.75, 140.46), "茨城県": (36.34, 140.44), "栃木県": (36.56, 139.88),
    "群馬県": (36.39, 139.06), "埼玉県": (35.85, 139.64), "千葉県": (35.60, 140.12),
    "東京都": (35.68, 139.69), "神奈川県": (35.44, 139.64), "新潟県": (37.90, 139.02),
    "富山県": (36.69, 137.21), "石川県": (36.59, 136.62), "福井県": (36.06, 136.22),
    "山梨県": (35.66, 138.56), "長野県": (36.65, 138.18), "岐阜県": (35.39, 136.72),
    "静岡県": (34.97, 138.38), "愛知県": (35.18, 136.90), "三重県": (34.73, 136.50),
