import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 🛠 診断＆セーフモード起動 ---
try:
    from kerykeion import KrInstance
    LIBRARY_LOADED = True
except ImportError:
    LIBRARY_LOADED = False

def main():
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")
    st.title("Aroma Soul Navigation 🌟")
    
    # --- ライブラリ読み込み失敗時の表示 ---
    if not LIBRARY_LOADED:
        st.error("⚠️ 重要な設定ファイルが読み込まれていません")
        st.warning("""
        **原因:** `requirements.txt` というファイルが見つからないか、名前が間違っています。
        
        **対策:** GitHubを見て、ファイル名が `requirements.txt.txt` になっていないか確認してください。
        
        ※現在は「セーフモード」で起動しています。占星術の計算機能はオフになっていますが、香りの入力は可能です。
        """)
    else:
        st.success("✅ システム正常稼働中：すべての機能が使えます")

    st.markdown("### 星（先天的な資質）と 香り（現在の状態）のバランス分析")

    # --- サイドバー入力 ---
    with st.sidebar:
        st.header("1. 出生データの入力")
        name = st.text_input("お名前", "Guest")
        b_year = st.number_input("年", 1950, 2025, 1990)
        b_month = st.number_input("月", 1, 12, 1)
        b_day = st.number_input("日", 1, 31, 1)
        b_hour = st.number_input("時 (24時間制)", 0, 23, 12)
        b_min = st.number_input("分", 0, 59, 0)
        city = st.text_input("出生都市 (ローマ字)", "Tokyo")
        nation = st.text_input("国コード (JP, US等)", "JP")
        
        st.markdown("---")
        st.header("2. 香りのチェック結果")
        scent_fire = st.number_input("火の香り", 0, 10, 0)
        scent_earth = st.number_input("地の香り", 0, 10, 0)
        scent_air = st.number_input("風の香り", 0, 10, 0)
        scent_water = st.number_input("水の香り", 0, 10, 0)

        calc_btn = st.button("分析する")

    # --- 計算ロジック ---
    if calc_btn:
        # 香りのスコア集計
        scent_values = [scent_fire, scent_earth, scent_air, scent_water]
        
        # 星のスコア集計（ライブラリがある場合のみ計算）
        astro_scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        details = []
        
        if LIBRARY_LOADED:
            try:
                # --- ここから占星術計算 ---
                # 設定: 4元素と星座
                ELEMENTS = {"Fire": ["Ari", "Leo", "Sag"], "Earth": ["Tau", "Vir", "Cap"], "Air": ["Gem", "Lib", "Aqr"], "Water": ["Can", "Sco", "Pis"]}
                ELEMENT_JP = {"Fire": "火 (直感/情熱)", "Earth": "地 (感覚/現実)", "Air": "風 (思考/情報)", "Water": "水 (感情/共感)"}
                PLANET_SCORES = {"Sun": 5, "Moon": 5, "Asc": 5, "Mc": 5, "Mercury": 3, "Venus": 3, "Mars": 3, "Jupiter": 2, "Saturn": 2, "Uranus": 1, "Neptune": 1, "Pluto": 1}
                
                def get_element(sign_abbr):
                    for e, s in ELEMENTS.items():
                        if sign_abbr in s: return e
                    return None

                user = KrInstance(name, b_year, b_month, b_day, b_hour, b_min, city, nation)
                target_points = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

                for planet_name in target_points:
                    p_data = user.get_planet(planet_name)
                    sign = p_data["sign"]
                    elem = get_element(sign)
                    score = PLANET_SCORES.get(planet_name, 0)
                    if elem:
                        astro_scores[elem] += score
                        details.append(f"{planet_name} ({sign}) -> {ELEMENT_JP[elem]}: +{score}")

                asc_sign = user.first_house["sign"]
                mc_sign = user.tenth_house["sign"]
                astro_scores[get_element(asc_sign)] += PLANET_SCORES["Asc"]
                details.append(f"ASC ({asc_sign}) -> {ELEMENT_JP[get_element(asc_sign)]}: +{PLANET_SCORES['Asc']}")
                astro_scores[get_element(mc_sign)] += PLANET_SCORES["Mc"]
                details.append(f"MC ({mc_sign}) -> {ELEMENT_JP[get_element(mc_sign)]}: +{PLANET_SCORES['Mc']}")
                # --- 計算ここまで ---
                
            except Exception as e:
                st.error(f"計算エラー: {e}")
        else:
            # ライブラリがない場合のダミーデータ（エラー回避用）
            st.info("⚠️ 占星術の計算機能は現在オフです（設定ファイル未読み込みのため）")

        # --- 結果表示 ---
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"{name}様の分析")
            if details:
                with st.expander("星の計算詳細"):
                    for d in details: st.write(d)
            
            # グラフ用のラベル定義
            labels = ["火 (Fire)", "地 (Earth)", "風 (Air)", "水 (Water)"]
            colors = ['#FF6B6B', '#4ECDC4', '#A8D8EA', '#3C40C6']
            
            # 星のデータ（計算できなければオール0）
            astro_values = [astro_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]

        with col2:
            st.subheader("バランスシート")
            fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                subplot_titles=['星 (先天的)', '香り (現在)'])
            
            # 左：星のグラフ
            if sum(astro_values) > 0:
                fig.add_trace(go.Pie(labels=labels, values=astro_values, name="Astro", marker_colors=colors, hole=.3), 1, 1)
            else:
                # データがない時は空の円を表示
                fig.add_trace(go.Pie(labels=labels, values=[1,1,1,1], name="No Data", marker_colors=['#eee']*4, hole=.3, textinfo='none'), 1, 1)

            # 右：香りのグラフ
            if sum(scent_values) > 0:
                fig.add_trace(go.Pie(labels=labels, values=scent_values, name="Scent", marker_colors=colors, hole=.3), 1, 2)
            
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
