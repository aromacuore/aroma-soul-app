import streamlit as st
import os
import sys

st.set_page_config(page_title="環境診断モード")
st.title("🕵️‍♀️ 最終診断モード")

st.markdown("### 1. Pythonバージョンの確認")
v = sys.version_info
version_str = f"{v.major}.{v.minor}"
st.write(f"現在のバージョン: **{version_str}**")

if v.minor >= 12:
    st.error("❌ Pythonが新しすぎます（3.13などになっています）")
    st.warning("原因: `runtime.txt` が正しく作られていないか、名前が間違っています。")
else:
    st.success(f"✅ Pythonバージョンは正常です（{version_str}）")

st.markdown("---")
st.markdown("### 2. ファイル名の確認")
files = os.listdir('.')
st.write("📂 サーバーにあるファイル一覧:")
st.code(files)

# runtime.txt のチェック
if "runtime.txt" in files:
    st.success("✅ runtime.txt は存在します！")
    with open("runtime.txt", "r") as f:
        content = f.read().strip()
    st.write("中身:")
    st.code(content)
    
    if "python-3.9" in content:
        st.success("✅ 中身も完璧です。")
    else:
        st.error("❌ 中身が `python-3.9` ではありません。書き直してください。")
else:
    st.error("❌ runtime.txt が見つかりません！")
    
    # 犯人捜し
    if "runtime.txt.txt" in files:
        st.error("🚨 犯人はこれです！ → `runtime.txt.txt`")
        st.info("対策: GitHubでこのファイルの名前変更を選び、後ろの .txt を1つ消してください。")
    elif "Runtime.txt" in files:
        st.error("🚨 犯人はこれです！ → `Runtime.txt`（大文字になっている）")
        st.info("対策: すべて小文字の `runtime.txt` に直してください。")
    else:
        st.info("対策: GitHubで「Add file」から `runtime.txt` を新しく作ってください。")

st.markdown("---")
st.write("診断が終わったら、GitHubでファイル名を修正し、もう一度アプリを削除＆再作成してください。")
