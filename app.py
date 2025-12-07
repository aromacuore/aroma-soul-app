import streamlit as st
import sys
import subprocess
import os
import time

# --- 🕵️‍♀️ 究極の診断＆修復モード ---

def install_and_retry():
    """ライブラリがない場合に強制インストールする関数"""
    st.title("⚙️ 初回セットアップ中...")
    st.info("必要な機能をインストールしています。このまま約1〜2分お待ちください。")
    
    # プログレスバー表示
    my_bar = st.progress(0)
    
    try:
        # 1. pipのアップグレード
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        my_bar.progress(20)
        
        # 2. 必要なライブラリのインストール
        packages = ["plotly", "pandas", "pyswisseph", "kerykeion"]
        for i, pkg in enumerate(packages):
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            my_bar.progress(20 + (i+1) * 20)
            
        st.success("✅ インストール完了！ 自動的に起動します...")
        time.sleep(1)
        st.rerun()
        
    except subprocess.CalledProcessError as e:
        # インストールに失敗した場合（Pythonのバージョン問題など）
        st.error("❌ インストールに失敗しました")
        st.error(f"エラー内容: {e}")
        
        # Pythonバージョンのチェック
        ver = sys.version_info
        st.warning(f"現在のPythonバージョン: {ver.major}.{ver.minor}")
        
        if ver.minor >= 12:
            st.error("⚠️ 原因特定: Pythonのバージョンが新しすぎます（3.12以上はエラーになります）。")
            st.info("""
            **【解決策】**
            GitHubに `runtime.txt` というファイルを作り、中身に `python-3.9` とだけ書いて保存してください。
            その後、アプリを作り直してください。
            """)
        st.stop()

# --- ライブラリの読み込みチェック ---
try:
    import plotly.graph_objects as go
    from kerykeion import KrInstance
    import pandas as pd
    from plotly.subplots import make_subplots
except ImportError:
    # 読み込めない場合はインストールを実行
    install_and_retry()

# --- 🌟 ここから下が本番アプリ（インストール成功時のみ動く） ---

# 設定: 4元素と星座の対応
ELEMENTS = {
    "Fire": ["Ari", "Leo", "Sag"],
    "Earth": ["Tau", "Vir", "Cap"],
    "Air": ["Gem", "Lib", "Aqr"],
    "Water": ["Can", "Sco", "Pis"]
}

ELEMENT_JP = {
    "Fire": "火 (直感/情熱)",
    "Earth": "地 (感覚/現実)",
    "Air": "風 (思考/情報)",
    "Water": "水 (感情/共感)"
}

PLANET_SCORES = {
    "Sun": 5, "Moon": 5, "Asc": 5, "Mc": 5,
    "Mercury": 3, "Venus": 3, "Mars": 3,
    "Jupiter": 2, "Saturn": 2,
    "Uranus": 1, "Neptune": 1, "Pluto": 1
}

def get_element(sign_abbr):
    for element, signs in ELEMENTS.items():
        if sign_abbr in signs:
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
        city = st.text_input("出生都市 (ローマ字)", "Tokyo")
        nation = st.text_input("国コード (JP, US等)", "JP")
        
        st.markdown("---")
        st.header("2. 香りのチェック結果")
        scent_fire = st.number_input("火の香り", 0, 10, 0)
        scent_earth = st.number_input("地の香り", 0, 10, 0)
        scent_air = st.number_input("風の香り", 0, 10, 0)
        scent_water = st.number_input("水の香り", 0, 10, 0)

        calc_btn = st.button("分析する")

    if calc_btn:
        try:
            user = KrInstance(name, b_year, b_month, b_day, b_hour, b_min, city, nation)
            
            target_points = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
                             "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

            astro_scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
            details = []

            for planet_name in target_points:
                planet_data = user.get_planet(planet_name)
                sign = planet_data["sign"]
                element = get_element(sign)
                score = PLANET_SCORES.get(planet_name, 0)
                if element:
                    astro_scores[element] += score
                    details.append(f"{planet_name} ({sign}) -> {ELEMENT_JP[element]}: +{score}点")

            asc_sign = user.first_house["sign"]
            mc_sign = user.tenth_house["sign"]
            
            asc_elem = get_element(asc_sign)
            astro_scores[asc_elem] += PLANET_SCORES["Asc"]
            details.append(f"ASC ({asc_sign}) -> {ELEMENT_JP[asc_elem]}: +{PLANET_SCORES['Asc']}点")

            mc_elem = get_element(mc_sign)
            astro_scores[mc_elem] += PLANET_SCORES["Mc"]
            details.append(f"MC ({mc_sign}) -> {ELEMENT_JP[mc_elem]}: +{PLANET_SCORES['Mc']}点")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader(f"{name}様の 天体スコア内訳")
                st.info(f"出生地: {city}, {nation} / 時間: {b_hour}:{b_min}")
                with st.expander("詳細な計算内容を見る"):
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
                st.plotly_chart
