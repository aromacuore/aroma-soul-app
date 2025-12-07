import streamlit as st
import os

st.set_page_config(page_title="システム診断モード")
st.title("🕵️‍♀️ システム診断モード")

st.info("サーバーの中にあるファイルを調べています...")

# 1. フォルダにある全ファイルを表示
files = os.listdir('.')
st.write("📂 現在のファイル一覧:")
st.code(files)

# 2. requirements.txt の捜索
target = "requirements.txt"

if target in files:
    st.success(f"✅ {target} は正しく存在します！")
    
    # 中身のチェック
    with open(target, "r") as f:
        content = f.read()
    st.write("📄 ファイルの中身:")
    st.code(content)
    
    if "kerykeion" in content:
        st.success("✅ 中身も完璧です！")
        st.balloons()
        st.markdown("### 🎉 診断結果：システムは正常です")
        st.write("この画面が出ているなら、準備は整っています。次のステップで本番コードに戻しましょう。")
    else:
        st.error(f"❌ ファイルはありますが、中に 'kerykeion' が書かれていません！")
        st.write("GitHubで requirements.txt を編集して、kerykeion と書き加えてください。")

else:
    st.error(f"❌ {target} が見つかりません！")
    
    # 似ている名前を探す（これが犯人の可能性大！）
    found_similar = False
    for f in files:
        if "requirement" in f.lower():
            st.warning(f"⚠️ 似ているファイルを見つけました: 【 {f} 】")
            if f == "requirements.txt.txt":
                st.error("犯人はこれです！「.txt」が2回重なっています。")
                st.write("対策：GitHubでこのファイルの名前変更を選び、後ろの .txt を1つ消してください。")
            found_similar = True
            
    if not found_similar:
        st.error("requirements.txt というファイル自体が作られていないようです。GitHubで「Add file」から作ってください。")
