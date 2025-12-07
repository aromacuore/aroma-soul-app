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
                with st.spinner(f'データ準備中... {filename}'):
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(filename, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                st.error(f"ダウンロードエラー: {e}")
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

ELEMENT_JP = {
    "Fire": "火 (胆汁質)",
    "Earth": "地 (神経質)",
    "Air": "風 (多血質)",
    "Water": "水 (リンパ質)"
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

# --- 1. Big 3の解説テキスト ---
BIG3_EXPLANATION = {
    "Sun": "あなたがこの世に生まれ持った「魂の核」であり、意識的に目指すべき人生のテーマです。社会の中で輝くための「表の顔」であり、迷った時に立ち返るべきエネルギーの源です。",
    "Moon": "あなたの無意識、感情、プライベートな素顔を表します。理屈ではなく「快・不快」を感じるセンサーであり、心がリラックスして満たされるために必要な要素です。",
    "Asc": "他者から見たあなたの第一印象や、無意識に出てしまう行動パターン、生まれ持った資質を表します。「世界への玄関口」とも呼ばれ、あなたが社会と接する際のマスク（仮面）のような役割を持ちます。"
}

# --- 2. 本来の資質（星）の定義 ---
STAR_DEFINITIONS = {
    "Fire": """
    **本来の資質:** 「決断力、行動力、情熱、自己信頼」といった火のエレメントを核に持つ、リーダーシップと目標達成能力に優れた資質です。\n
    **美点の活用:** 迷わず目標に向かって進む力が〇〇様の人生を推進します。
    """,
    "Earth": """
    **本来の資質:** 「安定性、堅実さ、継続力、現実的な実行力」といった土のエレメントを核に持つ、目標を確実に形にする力と、安心感を生み出す資質です。\n
    **美点の活用:** 現実の基礎を築き、ブレずに物事をやり遂げる力が〇〇様の人生を支えます。
    """,
    "Air": """
    **本来の資質:** 「社交性、柔軟性、好奇心、論理的な思考力」といった風のエレメントを核に持つ、コミュニケーション能力と、状況を多角的に捉える資質です。\n
    **美点の活用:** 軽やかに人と繋がり、新しい情報を取り入れ、人生に変化と広がりをもたらします。
    """,
    "Water": """
    **本来の資質:** 「共感力、受容性、優しさ、直感力」といった水のエレメントを核に持つ、他者の感情を深く理解し、調和を生み出す資質です。\n
    **美点の活用:** 場の雰囲気や人間関係を円滑にし、深い感情的な満足を人生にもたらします。
    """
}

# --- 3. パターン別診断メッセージ ---
PATTERN_MESSAGES = {
    "Fire": { 
        "title": "【パターン 1：水（リンパ質）の不足・火（胆汁質）の過剰タイプ】",
        "type": "🔥 胆汁質タイプ：本来の「火」が過剰になり、休息を求めている可能性",
        "detail": """
        * **苦手な香り（火）：** 心身が「火」のエレメントを拒否しているのは、ご自身のエネルギーが十分に満たされている証拠ですが、太陽星座が火のエレメント以外の場合は、怒りの感情の抑圧や心身の隠れた炎症を示している可能性もあります。
        * **好きな香り（水）：** 心身が「水」のエレメントを好むのは、本来の情熱（火）が過剰になり、休息やクールダウン、受容することを心身が強く求めているサインかもしれません。
        """,
        "cause": "〇〇様の【太陽星座の気質】の「決断力と情熱」が、過剰になりすぎて休息や調和（水）を求めている状態です。この火と水のアンバランスが、心身の疲弊や自己強制の罠を生み出し、迷いの原因となっている可能性があります。太陽星座が火のエレメントの方の通常モードではありますが、そうでない場合は、ご自身の心と体に怒りの感情の抑圧や隠れた炎症がないか向き合ってみてください。"
    },
    "Earth": {
        "title": "【パターン 2：土（神経質）の過剰・風（多血質）の不足タイプ】",
        "type": "🌏 神経質タイプ：本来の「土」が過剰になり、停滞感を感じている可能性",
        "detail": """
        * **苦手な香り（土）：** ご自身が「土」のエレメントを拒否しているのは、ご自身のエネルギーが十分に満たされている証拠ですが、太陽星座が土のエレメント以外の場合は、考えすぎて動けない時や疲れている時にラベンダーが苦手になります。楽しいことを取り入れるようにしましょう。
        * **好きな香り（風）：** 「風」の香りを好むのは、現状の安定した状態（土）に新しい風（風）を入れてバランスを取ろうとされているサインです。
        """,
        "cause": "〇〇様の【太陽星座の気質】（土）の「堅実な継続力」が、「変化への恐れ」に転じてしまい、柔軟な発想や行動力（風）が不足しています。この土と風のアンバランスが、同じ悩みを繰り返す停滞感を生み出し、迷いの原因となっている可能性があります。太陽星座が土のエレメントの方の通常モードではありますが、そうでない場合は、今が考えすぎて動けない時ではないか、ご自身の心と向き合ってみてください。"
    },
    "Air": {
        "title": "【パターン 3：風（多血質）の過剰・土（神経質）の不足タイプ】",
        "type": "🌬️ 多血質タイプ：本来の「風」が過剰になり、地に足がついていない可能性",
        "detail": """
        * **苦手な香り（風）：** 心身が「風」のエレメントを拒否しているのは、ご自身のエネルギーが十分に満たされている証拠ですが、太陽星座が風のエレメント以外の場合は、地に足をつけて安心したいのかもしれません。
        * **好きな香り（土）：** 「土」のラベンダー等を好むのは、さらに多くの情報や刺激を求めている一方で、足元を固めるための静かな時間（土）が圧倒的に不足している状態を示しています。
        """,
        "cause": "〇〇様の【太陽星座の気質】（風）の「社交性と柔軟性」が、「散漫さや軽薄さ」に転じてしまい、目標を現実的に実行するための安定感や集中力（土）が不足しています。このため土の香りが好ましいと感じます。この風と土のアンバランスが、空回りや目標達成の遅れを生み出し、迷いの原因となっている可能性があります。"
    },
    "Water": {
        "title": "【パターン 4：火（胆汁質）の不足・水（リンパ質）の過剰タイプ】",
        "type": "💧 リンパ質タイプ：本来の「水」が過剰になり、自己主張ができていない可能性",
        "detail": """
        * **苦手な香り（水）：** 心身が「水」のエレメントを拒否しているのは、〇〇様の「受容と調和（水）」を重視するあまり、自己主張や決断を下すことを心身が避けているサインかもしれません。
        * **好きな香り（火）：** 「火」の香りを好むのは、今の環境からさらに能動的になりたい、情熱をもって行動したいというニーズが強い一方で、自分から前に出るためのエネルギー（火）が圧倒的に不足している状態を示しています。
        """,
        "cause": "〇〇様の【太陽星座の気質】（水）の「優しさや共感力」が、「自己犠牲や受動性」に転じてしまい、自分の人生を自分で決め、情熱をもって行動するためのエネルギー（火）が不足しています。この水と火のアンバランスが、他者の意見に流されることによる迷いを生み出している可能性があります。"
    }
}

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

    if calc_btn:
        try:
            # 1. 星の計算
            date_str = f"{b_year}/{b_month:02d}/{b_day:02d}"
            time_str = f"{b_hour:02d}:{b_min:02d}"
            date = Datetime(date_str, time_str, '+09:00')
            lat, lon = PREFECTURES[city_name]
            pos = GeoPos(lat, lon)
            chart = Chart(date, pos, IDs=const.LIST_OBJECTS)

            sun_obj = chart.get(const.SUN)
            astro_sun_elem = get_element(sun_obj.sign)

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
            min_ranks = {"Fire": 9, "Earth": 9, "Air": 9, "Water": 9}
            max_ranks = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}

            for scent in SCENTS_CONF:
                rank = scent_ranks[scent["key"]]
                elem = scent["element"]
                scent_scores[elem] += rank
                if rank < min_ranks[elem]: min_ranks[elem] = rank
                if rank > max_ranks[elem]: max_ranks[elem] = rank

            # 診断ロジック
            core_star_elem = astro_sun_elem
            like_scent_elem = min(scent_scores.keys(), key=lambda k: (scent_scores[k], min_ranks[k]))
            dislike_scent_elem = max(scent_scores.keys(), key=lambda k: (scent_scores[k], -max_ranks[k]))
            pattern = PATTERN_MESSAGES[dislike_scent_elem]

            # --- 結果表示（レイアウト整理） ---
            st.header(f"📊 {name}様の分析レポート")
            
            # --- セクション1: 基本データ（Big3 & スコア） ---
            st.markdown("### 1. 魂の羅針盤 (Big 3) と バランス分析")
            
            # Big3表示
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**☀️ 太陽星座 ({SIGN_JP[sun_obj.sign]})**")
                st.caption(f"{BIG3_EXPLANATION['Sun']}")
            with c2:
                st.markdown(f"**🌙 月星座 ({SIGN_JP[chart.get(const.MOON).sign]})**")
                st.caption(f"{BIG3_EXPLANATION['Moon']}")
            with c3:
                st.markdown(f"**🏹 アセンダント ({SIGN_JP[chart.get(const.ASC).sign]})**")
                st.caption(f"{BIG3_EXPLANATION['Asc']}")
            
            st.markdown("---")

            # スコア表とグラフ
            col_g1, col_g2 = st.columns([1, 1.2])
            with col_g1:
                st.write("**【スコア内訳】**")
                df_res = pd.DataFrame([
                    {"性質": ELEMENT_JP[e], "星スコア": astro_scores[e], "香り順位合計": scent_scores[e]} 
                    for e in ["Fire", "Earth", "Air", "Water"]
                ])
                # スコアの説明を追加
                st.dataframe(df_res.set_index("性質"), use_container_width=True)
                st.caption("※香り順位合計：数字が小さいほど「好き」、大きいほど「苦手」を表します。")

            with col_g2:
                # グラフ
                labels_list = [ELEMENT_JP[k] for k in ["Fire", "Earth", "Air", "Water"]]
                colors_list = [COLORS[k] for k in ["Fire", "Earth", "Air", "Water"]]
                astro_values = [astro_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]
                scent_values = [scent_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]

                fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                    subplot_titles=['🪐 星の比率', '🌸 香りの比率'])
                fig.add_trace(go.Pie(labels=labels_list, values=astro_values, name="Astrology", marker_colors=colors_list, hole=.35), 1, 1)
                fig.add_trace(go.Pie(labels=labels_list, values=scent_values, name="Scent", marker_colors=colors_list, hole=.35), 1, 2)
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            # --- セクション2: 診断結果 ---
            st.markdown("---")
            st.markdown("### 2. 星と香りのズレ診断")
            
            # 重要な警告メッセージ
            st.warning("⚠️ **重要な法則**: 今、苦手だと感じる香りは、あなた自身の中に**過剰になっている性質**を表していることが多いです。")

            st.info(f"""
            **【ワークシート分析結果】**
            
            * **一番心地よかった香り**（今、心身が必要としているエネルギー）：  
              **{ELEMENT_JP[like_scent_elem]}** の香り ({OIL_NAMES[like_scent_elem]})
            * **一番苦手だった香り**（今、心身が拒否・抑圧しているエネルギー）：  
              **{ELEMENT_JP[dislike_scent_elem]}** の香り ({OIL_NAMES[dislike_scent_elem]})
            """)

            # 本来の資質
            st.markdown(f"**本来の資質：あなたは【{ELEMENT_JP[core_star_elem]}】の気質を持っています**")
            st.write(STAR_DEFINITIONS[core_star_elem].replace("〇〇様", f"{name}様"))

            # ズレの構造
            st.markdown(f"**今の状態：{pattern['type']}**")
            st.write(f"""
            {pattern['detail']}
            
            **💡 迷いの原因** {pattern['cause'].replace("〇〇様", f"{name}様")}
            """)

            # --- セクション3: 解決策 ---
            st.markdown("---")
            st.markdown("### 3. Navigation：ズレを解消し、美点として輝かせるために")
            st.write(f"""
            {name}様のこの「ズレ」は、決して直すべき欠点ではありません。  
            むしろ、本来の才能を活かすために必要な「エネルギーの調整」を心身が求めているサインです。
            
            **「{OIL_NAMES[like_scent_elem]}」** が求めるエネルギーを補い、  
            **「{OIL_NAMES[dislike_scent_elem]}」** が示す過剰なエネルギーを穏やかに整えることで、  
            {name}様が本来お持ちの **【{ELEMENT_JP[core_star_elem]}】** の才能（美点）は、迷いなく輝き始めます。
            
            ---
            **アロマクオーレ 本多さえこ**
            """)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
