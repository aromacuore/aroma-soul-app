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
    "滋賀県": (35.00, 135.86), "京都府": (35.02, 135.75), "大阪府": (34.68, 135.52),
    "兵庫県": (34.69, 135.18), "奈良県": (34.68, 135.80), "和歌山県": (34.22, 135.16),
    "鳥取県": (35.50, 134.23), "島根県": (35.47, 133.05), "岡山県": (34.66, 133.93),
    "広島県": (34.39, 132.46), "山口県": (34.18, 131.47), "徳島県": (34.06, 134.55),
    "香川県": (34.34, 134.04), "愛媛県": (33.84, 132.76), "高知県": (33.55, 133.53),
    "福岡県": (33.60, 130.41), "佐賀県": (33.24, 130.29), "長崎県": (32.74, 129.87),
    "熊本県": (32.78, 130.74), "大分県": (33.23, 131.61), "宮崎県": (31.91, 131.42),
    "鹿児島県": (31.56, 130.55), "沖縄県": (26.21, 127.68)
}

# --- 設定: 4元素と星座の対応 ---
ELEMENTS = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

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
        
        # 都市選択（47都道府県に変更）
        city_name = st.selectbox("出生地 (都道府県)", list(PREFECTURES.keys()))
        
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
            
            # 選択された都道府県の座標を取得
            lat, lon = PREFECTURES[city_name]
            pos = GeoPos(lat, lon)
            
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
