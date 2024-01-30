# StreamlitとOpenAIライブラリをインポート
import streamlit as st
import openai
import json

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    initial_content = str(st.secrets.AppSettings.chatbot_setting)
    st.session_state["messages"] = [
        {"role": "system", "content": initial_content}
    ]

## チャットボットとやりとりする関数
def communicate():
    if "user_input" in st.session_state and st.session_state["user_input"]:
        messages = st.session_state["messages"]

        user_message = {"role": "user", "content": st.session_state["user_input"]}
        messages.append(user_message)

        try:
            # ストリームレスポンスの取得
            stream_response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                messages=messages,
                stream=True
            )

            # 結果を逐次的に表示
            for chunk in stream_response:
                # 新しいチャンクの内容を取得
                next_content = chunk['choices'][0]['delta'].get('content', '')
                # 新しいメッセージをmessagesリストに追加
                if next_content.strip() != "":  # 空の内容は追加しない
                    bot_message = {"role": "assistant", "content": next_content}
                    messages.append(bot_message)
            
            # UIのメッセージ表示領域を更新
            update_message_display(messages)

        except Exception as e:
            st.error(f"APIリクエストでエラーが発生しました: {e}")
            st.write("エラー時のメッセージ履歴:")
            st.json(messages)
            return

        st.session_state["user_input"] = ""

# メッセージを表示する関数
def display_messages(messages):
    messages_container.empty()  # コンテナを一旦空にする
    complete_message = ""
    for message in messages:
        if message["role"] == "system":
            continue

        if message["role"] == "assistant":
            # 現在のメッセージを直前のメッセージに連結する
            complete_message += message["content"]
            # 文末がピリオド、クエスチョンマーク、エクスクラメーションマークなら表示する
            if complete_message.endswith(('.', '?', '!', '。', '？', '！')):
                messages_container.write(f"🤖 BOT: {complete_message}")
                complete_message = ""  # 表示した後はリセットする
        else:
            # ユーザーのメッセージはそのまま表示
            if complete_message:  # BOTのメッセージが完了していない場合は表示する
                messages_container.write(f"🤖 BOT: {complete_message}")
                complete_message = ""  # 表示した後はリセットする
            messages_container.write(f"🙂 YOU: {message['content']}")

# 以下のUI構築コードは変更なし
# ...
# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナ
messages_container = st.container()

if st.session_state.get("messages"):
    messages = st.session_state["messages"]

    for message in messages:
        # システムメッセージはスキップする
        if message["role"] == "system":
            continue

        speaker = "🙂YOU"
        if message["role"] == "assistant":
            speaker = "🤖BOT"

        content = message["content"]
        if not isinstance(content, str):
            content = str(content)

        messages_container.write(speaker + ": " + content)

# カスタムCSSを追加
st.markdown("""
    <style>
        .stTextArea > div > div > textarea {
            height: 50px; /* テキストボックスの高さ調整 */
            color: blue; /* テキストボックスのテキスト色 */
        }
        .stButton > button {
            height: 50px; /* ボタンの高さ調整 */
            color: blue; /* ボタンのテキスト色 */
            background-color: lightgray; /* ボタンの背景色 */
            vertical-align: low; /* ボタンの垂直方向の配置を中央に調整 */
        }
    </style>
    """, unsafe_allow_html=True)

# メッセージ入力（改行可能）と送信ボタンを横並びに配置
col1, col2 = st.columns([5, 1], gap="small")
with col1:
    user_input = st.text_area("メッセージを入力", key="user_input", height=100, placeholder="メッセージを入力してください。")
with col2:
    send_button = st.button("➤", key="send_button", on_click=communicate)

# Ctrl+Enterで送信するためのJavaScript
st.markdown("""
    <script>
        document.addEventListener("keydown", function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                document.querySelector('.stButton > button').click();
            }
        });
    </script>
    """, unsafe_allow_html=True)

# スクロール位置を最新のメッセージに自動調整するためのスクリプト
st.markdown(
    f"<script>const elements = document.querySelectorAll('.element-container:not(.stButton)');"
    f"elements[elements.length - 1].scrollIntoView();</script>",
    unsafe_allow_html=True,
)