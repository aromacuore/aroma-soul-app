import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import setPath  # ★ここを追加
import os
import requests

# --- 🛠 辞書ファイル（エフェメリス）の自動ダウンロード ---
def download_ephemeris():
    files = {
        "seas_18.se1": "https://github.com/pbrod/swisseph/raw/master/ephe/seas_18.se1",
        "semo_18.se1": "https://github.com/pbrod/swisseph/raw/master/ephe/semo_18.se1"
    }
    
    # フォルダにあるか確認し、なければダウンロード
    for filename, url in files.items():
        if not os.path.exists(filename):
            try:
                with st.spinner(f'星のデータを準備中... ({filename})'):
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(filename, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                st.error(f"データの準備に失敗しました: {e}")
                st.stop()

# 1. ダウンロードを実行
download_ephemeris()

# 2. ★重要：ダウンロードしたファイルの場所をflatlibに教える
setPath('.') 

# --- 🌟 ここから本番アプリ ---

# 設定: 4元素と星座の対応
ELEMENTS = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

# 表示ラベル設定
ELEMENT_JP = {
    "Fire": "火 (胆汁質)",
    "Earth": "地 (神経質)",
    "Air": "風 (多血質)",
    "Water": "水 (リンパ質)"
}
COLORS = {'Fire': '#FF6B6B', 'Earth': '#4ECDC4', 'Air': '#A8D8EA', 'Water': '#3C40C6'}

# 香りの定義
SCENTS_CONF = [
    {"element": "Fire", "name": "🔥 A (胆汁)", "key": "scent_a"},
    {"element": "Fire", "name": "🔥 B (胆汁)", "key": "scent_b"},
    {"element": "Air", "name": "🌬️ C (多血)", "key": "scent_c"},
    {"element": "Air", "name": "🌬️ D (多血)", "key": "scent_d"},
    {"element": "Earth", "name": "🌏 E (神経)", "key": "scent_e"},
    {"element": "Earth", "name": "🌏 F (神経)", "key": "scent_f"},
    {"element": "Water", "name": "💧 G (リンパ)", "key": "scent_g"},
    {"element": "Water", "name": "💧 H (リンパ)", "key": "scent_h"},
]

PLANET_SCORES = {
    "Sun": 5, "Moon": 5, "Asc": 5, "Mc": 5,
    "Mercury": 3, "Venus": 3, "Mars": 3,
    "Jupiter": 2, "Saturn": 2,
    "Uranus": 1, "Neptune": 1, "Pluto": 1
}

CITY_COORDS = {
    "Tokyo": (35.68, 139.76), "Osaka": (34.69, 135.50), "Nagoya": (35.18, 136.90),
    "Sapporo": (43.06, 141.35), "Fukuoka": (33.59, 130.40), "Naha": (26.21, 127.68),
    "Sendai": (38.26, 140.86)
}

def get_element(sign_name):
    for element, signs in ELEMENTS.items():
        if sign_name in signs: return element
    return None

def main():
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")
    st.title("Aroma Soul Navigation 🌟")
    st.markdown("### 星（先天的）と 香り（現在）の体質バランス比較")
    st.markdown("「好きな香りは自分から遠く、苦手な香りは自分に近い」という理論に基づく分析です。")

    # --- サイドバー入力 ---
    with st.sidebar:
        st.header("1. 出生データの入力")
        name = st.text_input("お名前", "Guest")
        col_b1, col_b2, col_b3 = st.columns(3)
        b_year = col_b1.number_input("年", 1950, 2025, 1990)
        b_month = col_b2.number_input("月", 1, 12, 1)
        b_day = col_b3.number_input("日", 1, 31, 1)
        col_b4, col_b5 = st.columns(2)
        b_hour = col_b4.number_input("時", 0, 23, 12)
        b_min = col_b5.number_input("分", 0, 59, 0)
        city_name = st.selectbox("出生都市", list(CITY_COORDS.keys()))
        
        st.markdown("---")
        st.header("2. 香りの順位チェック")
        st.write("8本の香りを嗅ぎ、好きな順に並べた結果（1位〜8位）を入力してください。")
        st.info("※ 1位＝最も好き、8位＝最も苦手")

        scent_ranks = {}
        current_element = None
        for scent in SCENTS_CONF:
            if current_element != scent["element"]:
                st.subheader(ELEMENT_JP[scent["element"]])
                current_element = scent["element"]
            default_rank = (SCENTS_CONF.index(scent) % 8) + 1
            rank = st.number_input(f"{scent['name']} の順位", 1, 8, default_rank, key=scent["key"])
            scent_ranks[scent["key"]] = rank

        st.markdown("---")
        calc_btn = st.button("分析する", type="primary")

    # --- 計算と表示 ---
    if calc_btn:
        try:
            # 1. 星の計算 (flatlib)
            date_str = f"{b_year}/{b_month:02d}/{b_day:02d}"
            time_str = f"{b_hour:02d}:{b_min:02d}"
            date = Datetime(date_str, time_str, '+09:00')
            pos = GeoPos(*CITY_COORDS[city_name])
            chart = Chart(date, pos, IDs=const.LIST_OBJECTS)

            astro_scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
            
            targets = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, 
                       const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO,
                       const.ASC, const.MC]
            target_names = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
                           "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "ASC", "MC"]

            for i, body_id in enumerate(targets):
                obj = chart.get(body_id)
                element = get_element(obj.sign)
                if element:
                    astro_scores[element] += PLANET_SCORES.get(target_names[i], 0)

            # 2. 香りの計算
            scent_scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
            for scent in SCENTS_CONF:
                scent_scores[scent["element"]] += scent_ranks[scent["key"]]

            # --- 結果表示 ---
            st.header(f"📊 {name}様の分析結果")
            
            col1, col2 = st.columns([1.2, 2])

            with col1:
                st.subheader("スコア内訳")
                df_res = pd.DataFrame([
                    {"Element": "Fire", "Label": ELEMENT_JP["Fire"], "星スコア": astro_scores["Fire"], "香り順位合計": scent_scores["Fire"]},
                    {"Element": "Earth", "Label": ELEMENT_JP["Earth"], "星スコア": astro_scores["Earth"], "香り順位合計": scent_scores["Earth"]},
                    {"Element": "Air", "Label": ELEMENT_JP["Air"], "星スコア": astro_scores["Air"], "香り順位合計": scent_scores["Air"]},
                    {"Element": "Water", "Label": ELEMENT_JP["Water"], "星スコア": astro_scores["Water"], "香り順位合計": scent_scores["Water"]},
                ])
                st.dataframe(df_res.set_index("Label"), use_container_width=True)

            with col2:
                st.subheader("バランス比較グラフ")
                labels_list = [ELEMENT_JP[k] for k in ["Fire", "Earth", "Air", "Water"]]
                colors_list = [COLORS[k] for k in ["Fire", "Earth", "Air", "Water"]]
                astro_values = [astro_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]
                scent_values = [scent_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]

                fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                    subplot_titles=['🪐 星の比率 (先天的体質)', '🌸 香りの比率 (現在の状態)'])

                fig.add_trace(go.Pie(
                    labels=labels_list, values=astro_values, name="Astrology",
                    marker_colors=colors_list, hole=.35,
                    hovertemplate="<b>%{label}</b><br>スコア: %{value}<br>割合: %{percent}"
                ), 1, 1)
                
                fig.add_trace(go.Pie(
                    labels=labels_list, values=scent_values, name="Scent",
                    marker_colors=colors_list, hole=.35,
                    hovertemplate="<b>%{label}</b><br>順位合計: %{value}位<br>割合: %{percent}"
                ), 1, 2)

                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
