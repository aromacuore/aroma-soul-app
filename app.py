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

# --- 🛠 関数定義（まだ実行はしない） ---
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

# --- 1. Big 3の解説テキスト ---
BIG3_EXPLANATION = {
    "Sun": "あなたがこの世に生まれ持った「魂の核」であり、意識的に目指すべき人生のテーマです。社会の中で輝くための「表の顔」であり、迷った時に立ち返るべきエネルギーの源です。",
    "Moon": "あなたの無意識、感情、プライベートな素顔を表します。理屈ではなく「快・不快」を感じるセンサーであり、心がリラックスして満たされるために必要な要素です。",
    "Asc": "他者から見たあなたの第一印象や、無意識に出てしまう行動パターン、生まれ持った資質を表します。「世界への玄関口」とも呼ばれ、あなたが社会と接する際のマスク（仮面）のような役割を持ちます。"
}

# --- 2. 本来の資質（星）の定義 ---
STAR_DEFINITIONS = {
    "Fire": """
    **【🔥 火の気質を多く持つ方の定義】**（胆汁質：牡羊座、獅子座、射手座など）  
    * **本来の資質:** 「決断力、行動力、情熱、自己信頼」といった火のエレメントを核に持つ、リーダーシップと目標達成能力に優れた資質です。
    * **美点の活用:** 迷わず目標に向かって進む力があなたの人生を推進します。
    """,
    "Earth": """
    **【🌏 土の気質を持つ方の定義】**（神経質：牡牛座、乙女座、山羊座など）  
    * **本来の資質:** 「安定性、堅実さ、継続力、現実的な実行力」といった土のエレメントを核に持つ、目標を確実に形にする力と、安心感を生み出す資質です。
    * **美点の活用:** 現実の基礎を築き、ブレずに物事をやり遂げる力があなたの人生を支えます。
    """,
    "Air": """
    **【🌬️ 風の気質を持つ方の定義】**（多血質：双子座、天秤座、水瓶座など）  
    * **本来の資質:** 「社交性、柔軟性、好奇心、論理的な思考力」といった風のエレメントを核に持つ、コミュニケーション能力と、状況を多角的に捉える資質です。
    * **美点の活用:** 軽やかに人と繋がり、新しい情報を取り入れ、人生に変化と広がりをもたらします。
    """,
    "Water": """
    **【💧 水の気質を持つ方の定義】**（リンパ質：蟹座、蠍座、魚座など）  
    * **本来の資質:** 「共感力、受容性、優しさ、直感力」といった水のエレメントを核に持つ、他者の感情を深く理解し、調和を生み出す資質です。
    * **美点の活用:** 場の雰囲気や人間関係を円滑にし、深い感情的な満足を人生にもたらします。
    """
}

# --- 3. 香りの好みで見える体質 (苦手＝過剰) ---
DISLIKE_ANALYSIS = {
    "Fire": """
    **【🔥 胆汁質タイプ】：「火」が過剰になり、休息を求めている可能性**
    * **苦手な香り:** [DISLIKE_OIL] など
    * 心身が「火」のエレメントを拒否しているのは、ご自身のエネルギーが十分に満たされている証拠ですが、太陽星座が火のエレメント以外の場合は、怒りの感情の抑圧や心身の隠れた炎症を示している可能性もあります。
    
    この場合「決断力と情熱」が、過剰になりすぎている状態です。この火のアンバランスが、心身の疲弊や自己強制の罠を生み出し、迷いの原因となっている可能性があります。太陽星座が火のエレメントの方の通常モードではありますが、そうでない場合は、ご自身の心と体に怒りの感情の抑圧や隠れた炎症がないか向き合ってみてください。
    """,
    "Earth": """
    **【🌏 神経質タイプ】：本来の「土」が過剰になり、停滞感を感じている可能性**
    * **苦手な香り:** [DISLIKE_OIL] など
    * ご自身が「土」のエレメントを拒否しているのは、ご自身のエネルギーが十分に満たされている証拠ですが、太陽星座が土のエレメント以外の場合は、考えすぎて動けない時や疲れている時にこの香りが苦手に感じます。
    
    **迷いの原因:** （土）の「堅実な継続力」が、「変化への恐れ」に転じてしまっています。この土のアンバランスが、同じ悩みを繰り返す停滞感を生み出し、迷いの原因となっている可能性があります。太陽星座が土のエレメントの方の通常モードではありますが、そうでない場合は、今が考えすぎて動けない時ではないか、ご自身の心身と向き合ってみてください。
    """,
    "Air": """
    **【🌬️ 多血質タイプ】：本来の「風」が過剰になり、地に足がついていない可能性**
    * **苦手な香り:** [DISLIKE_OIL] など
    * 心身が「風」のエレメントを拒否しているのは、ご自身のエネルギーが十分に満たされている証拠ですが、太陽星座が風のエレメント以外の場合は、地に足をつけて安心したいのかもしれません。
    
    **迷いの原因:** （風）の「社交性と柔軟性」が、「散漫さや軽薄さ」に転じてしまっています。この風のアンバランスが同じ悩みを繰り返す停滞感を生み出し、迷いの原因となっている可能性があります。
    
    太陽星座が風のエレメントの方の通常モードではありますが、そうでない場合は、今が散漫さや軽薄さがでていないか、ご自身の心身と向き合ってみてください。
    """,
    "Water": """
    **【💧 リンパ質タイプ】：「水」が過剰になり、自己主張ができていない可能性**
    * **苦手な香り:** [DISLIKE_OIL] など
    * 心身が「水」のエレメントを拒否しているのは、「受容と調和（水）」を重視するあまり、自己主張や決断を下すことを心身が避けているサインかもしれません。
    
    **迷いの原因:** （水）の「優しさや共感力」が、「自己犠牲や受動性」に転じてしまっています。この水のアンバランスが他者の意見に流されることによる迷いを生み出している可能性があります。
    
    太陽星座が水のエレメントの方の通常モードではありますが、そうでない場合は、今我慢しすぎていたり、人のために生きすぎているかもしれません。自分に優しい時間を取ってみてください。
    """
}

# --- 4. 好きな香りはあなたを調和させます (好き＝不足・薬) ---
LIKE_ANALYSIS = {
    "Fire": """
    * **好きな香り:** [LIKE_OIL] など
    * 「火」の香りを好むのは、今の環境からさらに能動的になりたい、情熱をもって行動したいというニーズが強い一方で、自分から前に出るためのエネルギー（火）が圧倒的に不足している状態を示しています。
    * 自分の人生を自分で決め、情熱をもって行動するためのエネルギー（火）をこの香りは持っています。
    * あなたの決断力行動力を支えます。
    """,
    "Earth": """
    * **好きな香り:** [LIKE_OIL] など
    * 「土」の香りを好むのは、地に足をつけて、冷静に過ごしたいときです。
    * 静かに五感が満たされる時間をすごしましょう。
    """,
    "Air": """
    * **好きな香り:** [LIKE_OIL] など
    * 「風」の香りを好むのは、現状に新しい風（風）を入れてバランスを取ろうとされているサインです。
    * 楽しいことを取り入れたり、考えすぎず執着せず緩く過ごしたいときです。
    """,
    "Water": """
    * **好きな香り:** [LIKE_OIL] など
    * 心身が「水」のエレメントを好むのは、休息やクールダウン、受容することを心身が強く求めているサインかもしれません。
    * 我慢しすぎていないか、体に炎症がないか、疲れすぎていないか、心身に聞いてみてください。
    """
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

# --- Main App ---
def main():
    # ★重要★ set_page_config は必ず一番最初に実行する
    st.set_page_config(page_title="Aroma Soul Navigation", layout="wide")

    # --- 🖨️ 印刷設定（PDF化のグラフ切れ・文字切れ防止 完全版） ---
    st.markdown("""
        <style>
        @media print {
            /* 1. 不要な要素を完全に消す */
            [data-testid="stSidebar"], .stButton, header, footer, [data-testid="stToolbar"] {
                display: none !important;
            }
            
            /* 2. 用紙のマージン設定 */
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

            /* 5. グラフのサイズ強制調整 */
            .js-plotly-plot, .plot-container, .main-svg {
                max-width: 100% !important;
                width: 100% !important;
                height: auto !important;
                margin: 0 auto !important;
                display: block !important;
            }
            
            .stPlotlyChart {
                page-break-inside: avoid;
            }

            /* 6. カラム崩れ防止 */
            [data-testid="column"] {
                width: 100% !important;
                display: block !important;
                page-break-inside: avoid !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # 初期化（データダウンロード）
    download_ephemeris()
    swe.set_ephe_path(os.getcwd())

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
            
            # 好きな香り(求めている): スコア小 & 順位高
            like_scent_elem = min(scent_scores.keys(), key=lambda k: (scent_scores[k], min_ranks[k]))
            
            # 苦手な香り(過剰・拒否): スコア大 & 順位低
            dislike_scent_elem = max(scent_scores.keys(), key=lambda k: (scent_scores[k], -max_ranks[k]))

            # --- 結果表示 ---
            st.header(f"【Aroma Soul Navigation 】あなたの「迷いの原因」分析レポート")
            st.write("「今の心身の状態」と「本来の資質」のズレを分析いたしました。")
            
            # --- Big 3 ---
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**☀️ 太陽 (本質)**")
                    st.write(f"### {SIGN_JP[sun_obj.sign]}")
                    st.caption(BIG3_EXPLANATION['Sun'])
                with c2:
                    st.markdown(f"**🌙 月 (内面)**")
                    st.write(f"### {SIGN_JP[chart.get(const.MOON).sign]}")
                    st.caption(BIG3_EXPLANATION['Moon'])
                with c3:
                    st.markdown(f"**🏹 ASC (外見)**")
                    st.write(f"### {SIGN_JP[chart.get(const.ASC).sign]}")
                    st.caption(BIG3_EXPLANATION['Asc'])

            st.write("") 

            # --- グラフとスコア ---
            col_g1, col_g2 = st.columns([1, 1.2])
            
            with col_g1:
                st.markdown("**スコア内訳**")
                df_res = pd.DataFrame([
                    {"性質": ELEMENT_JP[e], "星": astro_scores[e], "香り(順位計)": scent_scores[e]} 
                    for e in ["Fire", "Earth", "Air", "Water"]
                ])
                st.dataframe(df_res, hide_index=True, use_container_width=True)
                st.caption("※香り順位計：数字が小さいほど「好き」、大きいほど「苦手」")

            with col_g2:
                labels_list = [ELEMENT_JP[k] for k in ["Fire", "Earth", "Air", "Water"]]
                colors_list = [COLORS[k] for k in ["Fire", "Earth", "Air", "Water"]]
                astro_values = [astro_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]
                scent_values = [scent_scores[k] for k in ["Fire", "Earth", "Air", "Water"]]

                fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                    subplot_titles=['<b>星 (先天的)</b>', '<b>香り (現在)</b>'])
                fig.add_trace(go.Pie(labels=labels_list, values=astro_values, marker_colors=colors_list, hole=.4, showlegend=False), 1, 1)
                fig.add_trace(go.Pie(labels=labels_list, values=scent_values, marker_colors=colors_list, hole=.4, showlegend=False), 1, 2)
                fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            # --- 診断レポート ---
            st.markdown("---")
            
            st.markdown("#### 1. 分析結果の概要")
            st.info(f"""
            香り反応ワークで特に強い反応が出たのは以下の点でした。
            
            * **一番心地よかった香り**（今、心身が必要としているエネルギー）：  
              **{OIL_NAMES[like_scent_elem]}** ({ELEMENT_JP[like_scent_elem]})
            
            * **一番苦手だった香り**（今、心身が拒否・抑圧しているエネルギー）：  
              **{OIL_NAMES[dislike_scent_elem]}** ({ELEMENT_JP[dislike_scent_elem]})
            
            この結果から、あなたの「迷い」の正体が明確に見えてきました。
            
            本来のあなたは **【{ELEMENT_JP[core_star_elem]}】** の要素を持っています。  
            今のあなたの心身の過剰なところを表しているのは **【{ELEMENT_JP[dislike_scent_elem]}】**、  
            今のあなたが求めていることは **【{ELEMENT_JP[like_scent_elem]}】** です。
            """)

            st.markdown(f"#### 2. 本来の資質（星）の解釈：あなたの魂のバランス")
            st.write(f"まず、あなたが生まれ持った魂のバランス、すなわち【{ELEMENT_JP[core_star_elem]}】が持つ、本来の美点とエネルギーを定義します。")
            st.markdown(STAR_DEFINITIONS[core_star_elem])

            st.markdown(f"#### 3. 香りの好みで見える体質")
            # 苦手の分析
            dislike_text = DISLIKE_ANALYSIS[dislike_scent_elem].replace("[DISLIKE_OIL]", OIL_NAMES[dislike_scent_elem])
            st.warning(dislike_text)

            st.markdown("#### 【好きな香りはあなたを調和させます】")
            # 好きの分析
            like_text = LIKE_ANALYSIS[like_scent_elem].replace("[LIKE_OIL]", OIL_NAMES[like_scent_elem])
            st.success(like_text)

            st.divider()

            st.markdown(f"""
            「ズレ」は、決して直すべき欠点ではありません。  
            むしろ、本来の才能を活かすために必要な「エネルギーの調整」を心身が求めているサインです。
            
            好きな香りである **{ELEMENT_JP[like_scent_elem]}** の精油 **【{OIL_NAMES[like_scent_elem]}】** が求めるエネルギーを補い、  
            苦手な香りである **{ELEMENT_JP[dislike_scent_elem]}** の精油 **【{OIL_NAMES[dislike_scent_elem]}】** が示す過剰なエネルギーを穏やかに整えることで、  
            あなたが本来お持ちの **【{ELEMENT_JP[core_star_elem]}】** の才能（美点）は、迷いなく輝き始めます。
            """)
            
            st.write("")
            st.write("**アロマクオーレ 本多さえこ**")

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
