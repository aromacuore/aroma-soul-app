import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import swisseph as swe
import os
import requests

# --- 🖨️ 印刷設定（PDF化のグラフ切れ・文字切れ防止 完全版） ---
st.markdown("""
    <style>
    @media print {
        /* 1. 不要な要素を完全に消す */
        [data-testid="stSidebar"], .stButton, header, footer, [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* 2. 用紙のマージン設定（余白を少し減らしてスペース確保） */
        @page {
            size: A4;
            margin: 1cm;
        }

        /* 3. 全体のレイアウト調整 */
        .block-container {
            max-width: 100% !important;
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* 4. 文字の折り返し設定 */
        .stMarkdown, p, h1, h2, h3, h4, h5, h6, li, span, div {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }

        /* 5. 【重要】グラフのサイズ強制調整 */
        /* グラフ描画エリアを紙の幅に強制的に収める */
        .js-plotly-plot, .plot-container, .main-svg {
            max-width: 100% !important;
            width: 100% !important;
            height: auto !important;
            margin: 0 auto !important; /* 中央寄せ */
            display: block !important;
        }
        
        /* グラフがページをまたがないようにする */
        .stPlotlyChart {
            page-break-inside: avoid;
        }

        /* 6. カラム（段組み）の崩れ防止 */
        [data-testid="column"] {
            width: 100% !important;
            display: block !important;
            page-break-inside: avoid !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- 🛠 辞書ファイル（エフェメリス）の自動ダウンロード ---
def download_ephemeris():
    files = {
        "sepl_18.se1": "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/sepl_18.se1",
        "semo_18.se1": "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/semo_18.se1",
        "seas_18.se1": "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1"
    }
    for filename, url in files.items():
        if not os.path.exists(filename):
            try:
                with st.spinner(f'System initializing... {filename}'):
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(filename, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                st.error(f"System Error: {e}")
                st.stop()

download_ephemeris()
swe.set_ephe_path(os.getcwd())

# --- 🌟 辞書データ ---
SIGN_JP = {
    "Aries": "牡羊座", "Taurus": "牡牛座", "Gemini": "双子座", "Cancer": "蟹座",
    "Leo": "獅子座", "Virgo": "乙女座", "Libra": "天秤座", "Scorpio": "蠍座",
    "Sagittarius": "射手座", "Capricorn": "山羊座", "Aquarius": "水瓶座", "Pisces": "魚座"
}

PREFECTURES = {
    "北海道": (43.06, 141.35), "青森県": (40.82, 140.74), "岩手県": (39.70, 141.15),
    "宮城県": (38.26, 140.87), "秋田県": (39.71, 140.10), "山形県": (38.24, 140.36),
    "福島県": (37.75, 140.46), "茨城県": (36.34, 140.44), "栃木県": (36.56, 139.88),
    "群馬県": (36.39, 139.06), "埼玉県": (35.85, 139.64), "千葉県": (35.60, 140.12),
    "東京都": (35.68, 139.69), "神奈川県": (35.44, 139.64), "新潟県": (37.90, 139.02),
    "富山県": (36.69, 137.21), "石川県": (36.59, 136.62), "福井県": (36.06, 136.22),
    "山梨県": (35.66, 138.56), "長野県": (36.65, 138.18), "岐阜県": (35.39, 136.72),
    "静岡県": (34.97, 138.38), "愛知県": (35.18, 136.90), "三重県": (34.73, 136.50),
    "滋賀県": (35.00, 135.86), "京都府": (35.02, 135.75), "大阪府": (34.68, 135.52),
    "兵庫県": (34.69, 135.18), "奈良県": (34.68, 135.80), "和歌山県": (34.22, 135.16),
    "鳥取県": (35.50, 134.23), "島根県": (35.47, 133.05), "岡山県": (34.66, 133.93),
    "広島県": (34.39, 132.46), "山口県": (34.18, 131.47), "徳島県": (34.06, 134.55),
    "香川県": (34.34, 134.04), "愛媛県": (33.84, 132.76), "高知県": (33.55, 133.53),
    "福岡県": (33.60, 130.41), "佐賀県": (33.24, 130.29), "長崎県": (32.74, 129.87),
    "熊本県": (32.78, 130.74), "大分県": (33.23, 131.61), "宮崎県": (31.91, 131.42),
    "鹿児島県": (31.56, 130.55), "沖縄県": (26.21, 127.68)
}

ELEMENTS = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

# アイコンを設定（風を🌬️に戻しました）
ELEMENT_JP = {
    "Fire": "🔥 火 (胆汁質)",
    "Earth": "🌏 地 (神経質)",
    "Air": "🌬️ 風 (多血質)",
    "Water": "💧 水 (リンパ質)"
}

COLORS = {
    'Fire': '#FFCA99',  # ペールオレンジ
    'Earth': '#A4D65E', # 黄緑
    'Air': '#FFACC7',   # ピンク
    'Water': '#87CEEB'  # 水色
}

OIL_NAMES = {
    "Fire": "ローレル、ユーカリ・ラディアタ、オレンジ・スイート",
    "Earth": "ラベンダー・アングスティフォリア、カモマイル・ローマン、イランイラン",
    "Air": "ホーウッド、パルマローザ、マジョラム",
    "Water": "レモングラス、リトセア、ユーカリ・レモン、ローズマリー・カンファー"
}

# --- 1. Big 3
