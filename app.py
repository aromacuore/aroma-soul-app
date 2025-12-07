import streamlit as st
import sys
import os
import subprocess

st.set_page_config(page_title="最終診断")
st.title("🕵️‍♀️ 最終診断モード")

# --- 1. Pythonバージョンの確認 ---
st.header("1. Pythonバージョンの確認")
v = sys.version_info
version_str = f"{v.major}.{v.minor}"
st.write(f"現在のバージョン: **{version_str}**")

if v.minor >= 12:
    st.error("❌ Pythonが 3.13 (または12以上) です！")
    st.warning("これが原因でインストールが失敗しています。")
    st.info("対策: `runtime.txt` というファイルがないか、中身が間違っています。")
else:
    st.success(f"✅ Pythonバージョンは正常です (3.9)")

# --- 2. ファイル名の確認 ---
st.header("2. ファイル名の確認")
files = os.listdir('.')
st.code(files)

# requirements.txt チェック
if "requirements.txt" in files:
    st.success("✅ requirements.txt はあります")
else:
    st.error("❌ requirements.txt が見つかりません！")
    if "requirement.txt" in files:
        st.warning("⚠️ `requirement.txt` (sがない) になっています！")

# runtime.txt チェック
if "runtime.txt" in files:
    st.success("✅ runtime.txt はあります")
    with open("runtime.txt", "r") as f:
        content = f.read().strip()
    st.write(f"中身: {content}")
else:
    st.error("❌ runtime.txt が見つかりません！")

# --- 3. 強制インストール実験 ---
st.header("3. インストール実験")
if st.button("手動でインストールを試す"):
    st.write("インストールを開始します...")
    try:
        # 強制的にインストールコマンドを流して、エラーを見る
        result = subprocess.check_output(
            [sys.executable, "-m", "pip", "install", "kerykeion", "plotly", "pandas"],
            stderr=subprocess.STDOUT,
            encoding='utf-8'
        )
        st.success("インストール成功！")
        st.text(result)
    except subprocess.CalledProcessError as e:
        st.error("❌ インストール失敗")
        st.code(e.output) # ここに本当のエラー原因が出ます
