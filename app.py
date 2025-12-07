import streamlit as st
import sys
import subprocess
import os
import time

# --- 📦 初回セットアップ機能 ---
def auto_install():
    """必要なライブラリを強制インストールする"""
    st.title("⚙️ 初回セットアップ中...")
    st.warning("必要な機能をインストールしています。約1分お待ちください...")
    
    # プログレスバー
    bar = st.progress(0)
    
    try:
        # pip自体の更新
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        bar.progress(30)
        
        # ライブラリのインストール
        pkgs = ["plotly", "pandas", "pyswisseph", "kerykeion"]
        for i, pkg in enumerate(pkgs):
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            bar.progress(30 + (i+1)*15)
            
        st.success("✅ インストール完了！自動で起動します...")
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error("❌ インストール失敗")
        st.write(f"エラー: {e}")
        # バージョン警告
        v = sys.version_info
        if v.minor >= 12:
            st.error(f"原因: Python {v.major}.{v.minor} は新しすぎます。")
            st.info("解決策: GitHubに `runtime.txt` を作り `python-3.9` と書いて保存し、アプリを作り直してください。")
        st.stop()

# --- ライブラリ読み込みチェック ---
try:
    import plotly.graph_objects as go
    from kerykeion import KrInstance
    import pandas as pd
    from plotly.subplots import make_subplots
except ImportError:
    auto_install()

# --- 🌟 ここから本番アプリ ---
ELEMENTS = {"Fire": ["Ari","Leo","Sag"], "Earth": ["Tau","Vir","Cap"], "Air": ["Gem","Lib","Aqr"], "Water": ["Can","Sco","Pis"]}
ELEMENT_JP = {"Fire": "火 (直感)", "Earth": "地 (感覚)", "Air": "風 (思考)", "Water": "水 (感情)"}
PLANET_SCORES = {"Sun":5, "Moon":5, "Asc":5, "Mc":5, "Mercury":3, "Venus":3, "Mars":3, "Jupiter":2, "Saturn":2, "Uranus":1, "Neptune":1, "Pluto":1}

def get_element(sign):
    for e, s in ELEMENTS.items():
        if sign in s: return e
    return None

def main():
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")
    st.title("Aroma Soul Navigation 🌟")
    st.markdown("### 星（先天的）と 香り（現在）のバランス分析")

    with st.sidebar:
        st.header("1. 出生データ")
        name = st.text_input("お名前", "Guest")
        b_year = st.number_input("年", 1950, 2025, 1990)
        b_month = st.number_input("月", 1, 12, 1)
        b_day = st.number_input("日", 1, 31, 1)
        b_hour = st.number_input("時", 0, 23, 12)
        b_min = st.number_input("分", 0, 59, 0)
        city = st.text_input("都市 (ローマ字)", "Tokyo")
        nation = st.text_input("国 (JP等)", "JP")
        
        st.markdown("---")
        st.header("2. 香りチェック")
        s_fire = st.number_input("火の香り", 0, 10, 0)
        s_earth = st.number_input("地の香り", 0, 10, 0)
        s_air = st.number_input("風の香り", 0, 10, 0)
        s_water = st.number_input("水の香り", 0, 10, 0)
        calc_btn = st.button("分析する")

    if calc_btn:
        try:
            # 1. 占星術計算
            user = KrInstance(name, b_year, b_month, b_day, b_hour, b_min, city, nation)
            
            astro = {"Fire":0, "Earth":0, "Air":0, "Water":0}
            targets = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
            
            # 惑星スコア
            for p in targets:
                p_data = user.get_planet(p)
                elm = get_element(p_data["sign"])
                if elm: astro[elm] += PLANET_SCORES.get(p, 0)
            
            # ASC/MCスコア
            astro[get_element(user.first_house["sign"])] += 5
            astro[get_element(user.tenth_house["sign"])] += 5

            # 2. 表示
            c1, c2 = st.columns(2)
            with c1:
                st.subheader(f"{name}様の分析")
                st.info(f"{city}, {nation} / {b_year}.{b_month}.{b_day}")
                df = pd.DataFrame(list(astro.items()), columns=["Element", "Score"])
                df["Type"] = df["Element"].map(ELEMENT_JP)
                st.dataframe(df.set_index("Type"))

            with c2:
                st.subheader("バランス可視化")
                labels = [ELEMENT_JP[k] for k in astro.keys()]
                colors = ['#FF6B6B', '#4ECDC4', '#A8D8EA', '#3C40C6']
                v_astro = [astro[k] for k in ["Fire","Earth","Air","Water"]]
                v_scent = [s_fire, s_earth, s_air, s_water]

                fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                    subplot_titles=['星 (先天的)', '香り (現在)'])
                
                fig.add_trace(go.Pie(labels=labels, values=v_astro, name="Star", marker_colors=colors, hole=.3), 1, 1)
                if sum(v_scent) > 0:
                    fig.add_trace(go.Pie(labels=labels, values=v_scent, name="Scent", marker_colors=colors, hole=.3), 1, 2)
                
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

            # 3. メッセージ
            max_a = max(astro, key=astro.get)
            st.success(f"あなたの星は **{ELEMENT_JP[max_a]}** が最も強いです。")
            
            if sum(v_scent) > 0:
                scent_d = {"Fire":s_fire, "Earth":s_earth, "Air":s_air, "Water":s_water}
                max_s = max(scent_d, key=scent_d.get)
                if max_a == max_s:
                    st.write(f"香りも **{ELEMENT_JP[max_s]}** を選んでおり、資質を強調しています。")
                else:
                    st.write(f"星は **{ELEMENT_JP[max_a]}** ですが、香りは **{ELEMENT_JP[max_s]}** を求めています。")

        except Exception as e:
            st.error("エラーが発生しました")
            st.write(f"詳細: {e}")
            st.write("※都市名のスペル（Tokyoなど）を確認してください")

if __name__ == "__main__":
    main()
