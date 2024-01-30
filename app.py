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

# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# 上半分の空間を作成
st.empty()

# リアルタイムのストリームレスポンス用のプレースホルダーを中央に作成
stream_placeholder = st.empty()

# メッセージ表示用のコンテナ
messages_container = st.container()

# チャットボットとやりとりする関数
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

            # ストリームレスポンスを一時的な変数に保存
            streamed_text = ""
            for chunk in stream_response:
                next_content = chunk['choices'][0]['delta'].get('content', '')
                streamed_text += next_content

            # 完全なメッセージをプレースホルダーに書き込む
            stream_placeholder.write(streamed_text)

            # ストリームが完了したら、最終的なメッセージをmessagesに追加して表示
            bot_message = {"role": "assistant", "content": streamed_text}
            messages.append(bot_message)

        except Exception as e:
            st.error(f"APIリクエストでエラーが発生しました: {e}")
            st.write("エラー時のメッセージ履歴:")
            st.json(messages)

        # 入力フィールドをクリア
        st.session_state["user_input"] = ""

    # 会話履歴を更新
    display_messages(messages)

# 会話履歴を表示する関数
def display_messages(messages):
    messages_container.empty()  # コンテナを一旦空にする
    for message in messages:
        if message["role"] == "system":
            continue
        speaker = "🙂YOU" if message["role"] == "user" else "🤖BOT"
        messages_container.write(f"{speaker}: {message['content']}")

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

