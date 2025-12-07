import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from kerykeion import KrInstance
from plotly.subplots import make_subplots

# --- 設定: 4元素と星座の対応 ---
ELEMENTS = {
    "Fire": ["Ari", "Leo", "Sag"],  # 火: 牡羊, 獅子, 射手
    "Earth": ["Tau", "Vir", "Cap"], # 地: 牡牛, 乙女, 山羊
    "Air": ["Gem", "Lib", "Aqr"],   # 風: 双子, 天秤, 水瓶
    "Water": ["Can", "Sco", "Pis"]  # 水: 蟹, 蠍, 魚
}

# 日本語表示用マッピング
ELEMENT_JP = {
    "Fire": "火 (直感/情熱)",
    "Earth": "地 (感覚/現実)",
    "Air": "風 (思考/情報)",
    "Water": "水 (感情/共感)"
}

# --- 設定: 天体のスコア配分 (ユーザー定義) ---
# ※火星(Mars)は記載がなかったため、一般的な個人天体として3点に設定しています
PLANET_SCORES = {
    "Sun": 5, "Moon": 5, "Asc": 5, "Mc": 5,    # 最も重要
    "Mercury": 3, "Venus": 3, "Mars": 3,       # 次に重要
    "Jupiter": 2, "Saturn": 2,                 # 社会天体
    "Uranus": 1, "Neptune": 1, "Pluto": 1      # トランスサタニアン
}

def get_element(sign_abbr):
    """星座の略称からエレメントを返す関数"""
    for element, signs in ELEMENTS.items():
        if sign_abbr in signs:
            return element
    return None

def main():
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")
    
    st.title("Aroma Soul Navigation 🌟")
    st.markdown("### 星（先天的な資質）と 香り（現在の状態）のバランス分析")

    # --- サイドバー: 出生データの入力 ---
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
        st.write("選んだ香りの本数、または点数を入力してください")
        scent_fire = st.number_input("火の香り (本数/点)", 0, 10, 0)
        scent_earth = st.number_input("地の香り (本数/点)", 0, 10, 0)
        scent_air = st.number_input("風の香り (本数/点)", 0, 10, 0)
        scent_water = st.number_input("水の香り (本数/点)", 0, 10, 0)

        calc_btn = st.button("分析する")

    if calc_btn:
        try:
            # --- 1. ネイタルチャート計算 (kerykeion) ---
            user = KrInstance(name, b_year, b_month, b_day, b_hour, b_min, city, nation)
            
            # 必要な天体リスト
            target_points = [
                "Sun", "Moon", "Mercury", "Venus", "Mars", 
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
            ]

            # スコア集計用辞書
            astro_scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
            details = [] # 内訳表示用

            # 惑星の処理
            for planet_name in target_points:
                planet_data = user.get_planet(planet_name)
                sign = planet_data["sign"] # 略称を取得 (例: Ari)
                element = get_element(sign)
                score = PLANET_SCORES.get(planet_name, 0)
                
                if element:
                    astro_scores[element] += score
                    details.append(f"{planet_name} ({sign}) -> {ELEMENT_JP[element]}: +{score}点")

            # ASC / MC の処理 (ハウス情報から取得)
            # kerykeionではASCは第1ハウスカスプ、MCは第10ハウスカスプ
            asc_sign = user.first_house["sign"]
            mc_sign = user.tenth_house["sign"]
            
            # ASC
            asc_elem = get_element(asc_sign)
            astro_scores[asc_elem] += PLANET_SCORES["Asc"]
            details.append(f"ASC ({asc_sign}) -> {ELEMENT_JP[asc_elem]}: +{PLANET_SCORES['Asc']}点")

            # MC
            mc_elem = get_element(mc_sign)
            astro_scores[mc_elem] += PLANET_SCORES["Mc"]
            details.append(f"MC ({mc_sign}) -> {ELEMENT_JP[mc_elem]}: +{PLANET_SCORES['Mc']}点")

            # --- 2. 画面表示 ---
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader(f"{name}様の 天体スコア内訳")
                st.info(f"出生地: {city}, {nation} / 時間: {b_hour}:{b_min}")
                
                # スコア詳細を表示
                with st.expander("詳細な計算内容を見る"):
                    for d in details:
                        st.write(d)
                
                # データフレームで整理
                df_astro = pd.DataFrame(list(astro_scores.items()), columns=["Element", "Score"])
                df_astro["Label"] = df_astro["Element"].map(ELEMENT_JP)
                st.dataframe(df_astro.set_index("Label"))

            with col2:
                st.subheader("分析結果の可視化")
                
                # --- 円グラフの描画 (Plotly) ---
                labels = [ELEMENT_JP[k] for k in astro_scores.keys()]
                colors = ['#FF6B6B', '#4ECDC4', '#A8D8EA', '#3C40C6'] # 火, 地, 風, 水っぽい色
                
                # 星のスコア
                astro_values = [astro_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]
                
                # 香りのスコア
                scent_values = [scent_fire, scent_earth, scent_air, scent_water]

                fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                    subplot_titles=['星のスコア (先天的)', '香りのスコア (現在)'])

                fig.add_trace(go.Pie(labels=labels, values=astro_values, name="Astrology",
                                     marker_colors=colors, hole=.3), 1, 1)
                
                # 香りのスコアが全て0の場合は表示しないなどの処理が必要だが、今回はそのまま
                if sum(scent_values) > 0:
                    fig.add_trace(go.Pie(labels=labels, values=scent_values, name="Scent",
                                         marker_colors=colors, hole=.3), 1, 2)
                else:
                    st.warning("香りのデータが入力されていません")

                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

            # --- 3. 診断コメント ---
            st.markdown("### 💎 Navigation Message")
            max_astro = max(astro_scores, key=astro_scores.get)
            st.success(f"あなたの星の配置は **{ELEMENT_JP[max_astro]}** の要素が最も強いです。")
            
            if sum(scent_values) > 0:
                # 香りの最大値を取得（簡易ロジック）
                scent_dict = {"Fire": scent_fire, "Earth": scent_earth, "Air": scent_air, "Water": scent_water}
                max_scent = max(scent_dict, key=scent_dict.get)
                
                if max_astro == max_scent:
                    st.write(f"現在選んだ香りも **{ELEMENT_JP[max_scent]}** が多く、本来の資質を強調しています。自分らしく過ごせているか、あるいは過剰になっている可能性があります。")
                else:
                    st.write(f"星は **{ELEMENT_JP[max_astro]}** ですが、香りは **{ELEMENT_JP[max_scent]}** を求めています。今は本来の資質とは違う要素（{ELEMENT_JP[max_scent]}）を補う必要がある時期かもしれません。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.write("都市名のスペルなどを確認してください。")

if __name__ == "__main__":
    main()import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from kerykeion import KrInstance
from plotly.subplots import make_subplots

# --- 設定: 4元素と星座の対応 ---
ELEMENTS = {
    "Fire": ["Ari", "Leo", "Sag"],  # 火: 牡羊, 獅子, 射手
    "Earth": ["Tau", "Vir", "Cap"], # 地: 牡牛, 乙女, 山羊
    "Air": ["Gem", "Lib", "Aqr"],   # 風: 双子, 天秤, 水瓶
    "Water": ["Can", "Sco", "Pis"]  # 水: 蟹, 蠍, 魚
}

# 日本語表示用マッピング
ELEMENT_JP = {
    "Fire": "火 (直感/情熱)",
    "Earth": "地 (感覚/現実)",
    "Air": "風 (思考/情報)",
    "Water": "水 (感情/共感)"
}

# --- 設定: 天体のスコア配分 (ユーザー定義) ---
# ※火星(Mars)は記載がなかったため、一般的な個人天体として3点に設定しています
PLANET_SCORES = {
    "Sun": 5, "Moon": 5, "Asc": 5, "Mc": 5,    # 最も重要
    "Mercury": 3, "Venus": 3, "Mars": 3,       # 次に重要
    "Jupiter": 2, "Saturn": 2,                 # 社会天体
    "Uranus": 1, "Neptune": 1, "Pluto": 1      # トランスサタニアン
}

def get_element(sign_abbr):
    """星座の略称からエレメントを返す関数"""
    for element, signs in ELEMENTS.items():
        if sign_abbr in signs:
            return element
    return None

def main():
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")
    
    st.title("Aroma Soul Navigation 🌟")
    st.markdown("### 星（先天的な資質）と 香り（現在の状態）のバランス分析")

    # --- サイドバー: 出生データの入力 ---
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
        st.write("選んだ香りの本数、または点数を入力してください")
        scent_fire = st.number_input("火の香り (本数/点)", 0, 10, 0)
        scent_earth = st.number_input("地の香り (本数/点)", 0, 10, 0)
        scent_air = st.number_input("風の香り (本数/点)", 0, 10, 0)
        scent_water = st.number_input("水の香り (本数/点)", 0, 10, 0)

        calc_btn = st.button("分析する")

    if calc_btn:
        try:
            # --- 1. ネイタルチャート計算 (kerykeion) ---
            user = KrInstance(name, b_year, b_month, b_day, b_hour, b_min, city, nation)
            
            # 必要な天体リスト
            target_points = [
                "Sun", "Moon", "Mercury", "Venus", "Mars", 
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
            ]

            # スコア集計用辞書
            astro_scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
            details = [] # 内訳表示用

            # 惑星の処理
            for planet_name in target_points:
                planet_data = user.get_planet(planet_name)
                sign = planet_data["sign"] # 略称を取得 (例: Ari)
                element = get_element(sign)
                score = PLANET_SCORES.get(planet_name, 0)
                
                if element:
                    astro_scores[element] += score
                    details.append(f"{planet_name} ({sign}) -> {ELEMENT_JP[element]}: +{score}点")

            # ASC / MC の処理 (ハウス情報から取得)
            # kerykeionではASCは第1ハウスカスプ、MCは第10ハウスカスプ
            asc_sign = user.first_house["sign"]
            mc_sign = user.tenth_house["sign"]
            
            # ASC
            asc_elem = get_element(asc_sign)
            astro_scores[asc_elem] += PLANET_SCORES["Asc"]
            details.append(f"ASC ({asc_sign}) -> {ELEMENT_JP[asc_elem]}: +{PLANET_SCORES['Asc']}点")

            # MC
            mc_elem = get_element(mc_sign)
            astro_scores[mc_elem] += PLANET_SCORES["Mc"]
            details.append(f"MC ({mc_sign}) -> {ELEMENT_JP[mc_elem]}: +{PLANET_SCORES['Mc']}点")

            # --- 2. 画面表示 ---
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader(f"{name}様の 天体スコア内訳")
                st.info(f"出生地: {city}, {nation} / 時間: {b_hour}:{b_min}")
                
                # スコア詳細を表示
                with st.expander("詳細な計算内容を見る"):
                    for d in details:
                        st.write(d)
                
                # データフレームで整理
                df_astro = pd.DataFrame(list(astro_scores.items()), columns=["Element", "Score"])
                df_astro["Label"] = df_astro["Element"].map(ELEMENT_JP)
                st.dataframe(df_astro.set_index("Label"))

            with col2:
                st.subheader("分析結果の可視化")
                
                # --- 円グラフの描画 (Plotly) ---
                labels = [ELEMENT_JP[k] for k in astro_scores.keys()]
                colors = ['#FF6B6B', '#4ECDC4', '#A8D8EA', '#3C40C6'] # 火, 地, 風, 水っぽい色
                
                # 星のスコア
                astro_values = [astro_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]
                
                # 香りのスコア
                scent_values = [scent_fire, scent_earth, scent_air, scent_water]

                fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                    subplot_titles=['星のスコア (先天的)', '香りのスコア (現在)'])

                fig.add_trace(go.Pie(labels=labels, values=astro_values, name="Astrology",
                                     marker_colors=colors, hole=.3), 1, 1)
                
                # 香りのスコアが全て0の場合は表示しないなどの処理が必要だが、今回はそのまま
                if sum(scent_values) > 0:
                    fig.add_trace(go.Pie(labels=labels, values=scent_values, name="Scent",
                                         marker_colors=colors, hole=.3), 1, 2)
                else:
                    st.warning("香りのデータが入力されていません")

                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

            # --- 3. 診断コメント ---
            st.markdown("### 💎 Navigation Message")
            max_astro = max(astro_scores, key=astro_scores.get)
            st.success(f"あなたの星の配置は **{ELEMENT_JP[max_astro]}** の要素が最も強いです。")
            
            if sum(scent_values) > 0:
                # 香りの最大値を取得（簡易ロジック）
                scent_dict = {"Fire": scent_fire, "Earth": scent_earth, "Air": scent_air, "Water": scent_water}
                max_scent = max(scent_dict, key=scent_dict.get)
                
                if max_astro == max_scent:
                    st.write(f"現在選んだ香りも **{ELEMENT_JP[max_scent]}** が多く、本来の資質を強調しています。自分らしく過ごせているか、あるいは過剰になっている可能性があります。")
                else:
                    st.write(f"星は **{ELEMENT_JP[max_astro]}** ですが、香りは **{ELEMENT_JP[max_scent]}** を求めています。今は本来の資質とは違う要素（{ELEMENT_JP[max_scent]}）を補う必要がある時期かもしれません。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.write("都市名のスペルなどを確認してください。")

if __name__ == "__main__":
    main()