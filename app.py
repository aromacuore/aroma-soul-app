import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

# --- 設定: 4元素と星座の対応 (flatlib用) ---
ELEMENTS = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

ELEMENT_JP = {
    "Fire": "火 (直感/情熱)",
    "Earth": "地 (感覚/現実)",
    "Air": "風 (思考/情報)",
    "Water": "水 (感情/共感)"
}

# 天体のスコア配分
PLANET_SCORES = {
    "Sun": 5, "Moon": 5, "Asc": 5, "Mc": 5,
    "Mercury": 3, "Venus": 3, "Mars": 3,
    "Jupiter": 2, "Saturn": 2,
    "Uranus": 1, "Neptune": 1, "Pluto": 1
}

# 主要都市の緯度経度辞書（簡易版）
CITY_COORDS = {
    "Tokyo": (35.68, 139.76),
    "Osaka": (34.69, 135.50),
    "Nagoya": (35.18, 136.90),
    "Sapporo": (43.06, 141.35),
    "Fukuoka": (33.59, 130.40),
    "Naha": (26.21, 127.68),
    "Sendai": (38.26, 140.86),
    "Hiroshima": (34.38, 132.45),
    "Kanazawa": (36.56, 136.65)
}

def get_element(sign_name):
    for element, signs in ELEMENTS.items():
        if sign_name in signs:
            return element
    return None

def main():
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")
    st.title("Aroma Soul Navigation 🌟")
    st.markdown("### 星（先天的な資質）と 香り（現在の状態）のバランス分析")

    with st.sidebar:
        st.header("1. 出生データの入力")
        name = st.text_input("お名前", "Guest")
        b_year = st.number_input("年", 1950, 2025, 1990)
        b_month = st.number_input("月", 1, 12, 1)
        b_day = st.number_input("日", 1, 31, 1)
        b_hour = st.number_input("時 (24時間制)", 0, 23, 12)
        b_min = st.number_input("分", 0, 59, 0)
        
        # 都市選択（リストから選ぶ方式に変更）
        city_name = st.selectbox("出生都市", list(CITY_COORDS.keys()))
        
        st.markdown("---")
        st.header("2. 香りのチェック結果")
        scent_fire = st.number_input("火の香り", 0, 10, 0)
        scent_earth = st.number_input("地の香り", 0, 10, 0)
        scent_air = st.number_input("風の香り", 0, 10, 0)
        scent_water = st.number_input("水の香り", 0, 10, 0)
        calc_btn = st.button("分析する")

    if calc_btn:
        try:
            # --- 1. 新エンジン(flatlib)での計算 ---
            # 日付の作成
            date_str = f"{b_year}/{b_month:02d}/{b_day:02d}"
            time_str = f"{b_hour:02d}:{b_min:02d}"
            date = Datetime(date_str, time_str, '+09:00')
            
            # 場所の作成
            lat, lon = CITY_COORDS[city_name]
            pos = GeoPos(lat, lon)
            
            # チャート作成
            chart = Chart(date, pos, IDs=const.LIST_OBJECTS)

            astro_scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
            details = []

            # 惑星のループ
            targets = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, 
                       const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO]
            
            target_names = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
                           "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

            for i, body_id in enumerate(targets):
                planet = chart.get(body_id)
                sign = planet.sign
                element = get_element(sign)
                p_name = target_names[i]
                score = PLANET_SCORES.get(p_name, 0)
                
                if element:
                    astro_scores[element] += score
                    details.append(f"{p_name} ({sign}) -> {ELEMENT_JP[element]}: +{score}点")

            # ASC / MC (ハウス)
            asc = chart.get(const.ASC)
            mc = chart.get(const.MC)
            
            asc_elem = get_element(asc.sign)
            astro_scores[asc_elem] += PLANET_SCORES["Asc"]
            details.append(f"ASC ({asc.sign}) -> {ELEMENT_JP[asc_elem]}: +{PLANET_SCORES['Asc']}点")

            mc_elem = get_element(mc.sign)
            astro_scores[mc_elem] += PLANET_SCORES["Mc"]
            details.append(f"MC ({mc.sign}) -> {ELEMENT_JP[mc_elem]}: +{PLANET_SCORES['Mc']}点")

            # --- 2. 表示 ---
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader(f"{name}様の 天体スコア内訳")
                st.info(f"出生地: {city_name} / 時間: {b_hour}:{b_min}")
                with st.expander("詳細を見る"):
                    for d in details:
                        st.write(d)
                
                df_astro = pd.DataFrame(list(astro_scores.items()), columns=["Element", "Score"])
                df_astro["Label"] = df_astro["Element"].map(ELEMENT_JP)
                st.dataframe(df_astro.set_index("Label"))

            with col2:
                st.subheader("分析結果の可視化")
                labels = [ELEMENT_JP[k] for k in astro_scores.keys()]
                colors = ['#FF6B6B', '#4ECDC4', '#A8D8EA', '#3C40C6']
                astro_values = [astro_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]
                scent_values = [scent_fire, scent_earth, scent_air, scent_water]

                fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                    subplot_titles=['星のスコア (先天的)', '香りのスコア (現在)'])

                fig.add_trace(go.Pie(labels=labels, values=astro_values, name="Astrology", marker_colors=colors, hole=.3), 1, 1)
                
                if sum(scent_values) > 0:
                    fig.add_trace(go.Pie(labels=labels, values=scent_values, name="Scent", marker_colors=colors, hole=.3), 1, 2)
                else:
                    st.warning("香りのデータが未入力です")

                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

            # --- 3. メッセージ ---
            max_astro = max(astro_scores, key=astro_scores.get)
            strongest_element = ELEMENT_JP[max_astro]
            st.success(f"あなたの星の配置は **{strongest_element}** の要素が最も強いです。")
            
            if sum(scent_values) > 0:
                scent_dict = {"Fire": scent_fire, "Earth": scent_earth, "Air": scent_air, "Water": scent_water}
                max_scent = max(scent_dict, key=scent_dict.get)
                strongest_scent = ELEMENT_JP[max_scent]
                
                if max_astro == max_scent:
                    st.write(f"現在選んだ香りも **{strongest_scent}** が多く、本来の資質を強調しています。")
                else:
                    st.write(f"星は **{strongest_element}** ですが、香りは **{strongest_scent}** を求めています。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
