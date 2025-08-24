# 必要なライブラリをインポート
import streamlit as st  # Webアプリ作成用
import random  # ランダム選択用
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 認証スコープ
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# secrets.toml から認証情報を取得
creds_dict = st.secrets["gspread"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# スプレッドシートに接続（タイトルはGoogle Sheets上の名前と一致させる）
sheet = client.open_by_key("1G3eIkMW8rmrrKH9XzuRJb9Scek4MD4czE6TVpyDkHPM").worksheet("sheet1")
# ページ設定
st.set_page_config(
    page_title="同棲ほしいものリスト" , # ブラウザのタブに表示されるタイトル
    page_icon="🏠",                            # ブラウザのタブに表示されるアイコン
    layout="wide"                              # レイアウトをワイドに設定
)

# タイトルと説明
st.title("🏠　同棲ほしいものリスト")  # メインタイトル
st.markdown("---")  # 区切り線
st.markdown("### これいいと思った物をひたすら貼ってく！")  # サブタイトル



# ===== セッション状態の初期化 =====
# session_state：ページを更新してもデータを保持するStreamlitの機能
# 買い物リストを保存するための空のリストを作成
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = []  # 空のリストで初期化

# 削除確認メッセージを表示するためのフラグ
if 'clear_clicked' not in st.session_state:
    st.session_state.clear_clicked = False  # Falseで初期化

if 'favorites' not in st.session_state:
    st.session_state.favorites = []
# ===== 基本的な使用例 =====
# 辞書の場合
my_dict = {"name": "John", "age": 25}

# in演算子（存在するかチェック）
if "name" in my_dict:
    print(f"名前: {my_dict['name']}")  # 存在する場合の処理

# not in演算子（存在しないかチェック）
if "city" not in my_dict:
    my_dict["city"] = "Tokyo"  # 存在しない場合の処理

# リストの場合
my_list = ["apple", "banana", "orange"]

# in演算子（存在するかチェック）
if "apple" in my_list:
    print("りんごが見つかりました！")

# not in演算子（存在しないかチェック）
if "grape" not in my_list:
    my_list.append("grape")  # 存在しない場合の処理

# ===== メインコンテンツ =====
st.header("📝 買い物リスト管理")  # メインのヘッダー

# ユーザー名の入力欄（追加者の名前）
user_options = ["ゆうと", "なつみ"]
selected_user = st.selectbox("👤 あなたの名前を選択してください", user_options)
#カテゴリの選択
category_options = ["家電", "家具", "食器", "食品", "日用品", "その他"]
selected_category = st.selectbox("📦 カテゴリを選択してください", category_options)

# 新しいアイテムの入力
# st.text_input()：テキスト入力欄を作成
new_item = st.text_input("アイテムのリンクを貼ってください:", placeholder="URL")

# ===== 追加ボタンの処理 =====
# st.button()：ボタンを作成
if st.button("➕ リストに追加"):
    if new_item and selected_category:
        st.session_state.shopping_list.append(f"{new_item}（{selected_category} / by {selected_user}）")
        st.success(f"✅ '{new_item}' を追加（{selected_category} / {selected_user}）")

        try:
            sheet.append_row([new_item, selected_user, selected_category])
            st.info("📝 Google Sheetsにも保存しました！")
        except Exception as e:
            st.error(f"❌ Google Sheetsへの保存に失敗しました: {e}")
    else:
        st.warning("⚠️ アイテムとカテゴリを選択してください。")


# ===== クリアメッセージの表示 =====
# セッション状態を使ってメッセージを管理
# クリアボタンが押されたらメッセージを表示
if st.session_state.clear_clicked:
    st.success("✅ リストをクリアしました！")
    # メッセージを表示したらフラグをリセット（ボタンが押されていない状態にする）
    st.session_state.clear_clicked = False  # フラグをリセット

# Google Sheetsからデータ取得
rows = sheet.get_all_values()

# ===== 買い物リストの表示 =====
import pandas as pd

# データフレームに変換
df = pd.DataFrame(rows, columns=["アイテム", "追加者", "カテゴリ"])
# 追加者フィルター
unique_users = df["追加者"].unique().tolist()
selected_user = st.selectbox("👤 表示する追加者を選択", ["すべて表示"] + user_options)

# カテゴリフィルター
unique_categories = df["カテゴリ"].unique().tolist()
selected_category = st.selectbox("📦 表示するカテゴリを選択", ["すべて表示"] + unique_categories)

# Streamlitで表示
filtered_df = df.copy()

if selected_user != "すべて表示":
    filtered_df = filtered_df[filtered_df["追加者"] == selected_user]

if selected_category != "すべて表示":
    filtered_df = filtered_df[filtered_df["カテゴリ"] == selected_category]
st.subheader("🛒 絞り込み結果")
#st.dataframe(filtered_df)

# ===== リストが空の場合のメッセージ =====
if len(st.session_state.shopping_list) == 0:
    st.info("📝 まだアイテムがありません。上記の入力欄からアイテムを追加してみましょう！")
else:
    # ===== for文を使ってリストの中身を順番に表示 =====
    # enumerate()関数：リストの要素とインデックスを同時に取得
    # enumerate(st.session_state.shopping_list, 1)：インデックスを1から開始
    # これが今回の学習ポイントの1つ！
  for index, item in enumerate(st.session_state.shopping_list, 1):
    col1, col2, col3, col4 = st.columns([0.1, 0.5, 0.2, 0.2])

    with col1:
        st.write(f"**{index}.**")

    with col2:
        st.write(item)

    with col3:
        if item in st.session_state.favorites:
            if st.button("❌ お気に入り解除", key=f"unfav_{index}"):
                st.session_state.favorites.remove(item)
                st.rerun()
        else:
            if st.button("⭐ お気に入り", key=f"fav_{index}"):
                st.session_state.favorites.append(item)
                st.rerun()

    with col4:
        with st.popover("🗑️ 削除", help=f"「{item}」を削除"):
            st.write(f"「{item}」を削除しますか？")
            if st.button("はい", key=f"confirm_yes_{index}"):
                st.session_state.shopping_list.pop(index - 1)
                st.rerun()



# ===== リストの操作ボタン =====
if len(st.session_state.shopping_list) > 0:
    st.markdown("---")  # 区切り線
    # 2つのカラムを作成
    col1, col2 = st.columns(2)

    with col1:
        # リストをクリアするボタン
        if st.button("🗑️ リストをクリア"):
            # clear()メソッド：リストの全要素を削除
            st.session_state.shopping_list.clear()
            st.session_state.clear_clicked = True  # メッセージ表示フラグを設定
            st.rerun()  # ページを再読み込み

    with col2:
        # リストをコピーするボタン
        if st.button("📋 リストをコピー"):
            # リストの要素を文字列に変換
            # enumerate()関数：インデックスと要素を同時に取得
            # join()メソッド：リストの要素を改行で結合
            list_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(st.session_state.shopping_list)])
            st.code(list_text)  # コードブロックとして表示

            st.info("上記のリストをコピーして使用してください！")

















