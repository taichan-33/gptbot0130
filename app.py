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

def communicate():
    if "user_input" in st.session_state and st.session_state["user_input"]:
        user_message = {"role": "user", "content": st.session_state["user_input"]}
        st.session_state["messages"].append(user_message)

        try:
            # ストリームレスポンスの取得
            stream_response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                messages=st.session_state["messages"],
                stream=True
            )

            # 結果を逐次的にmessagesに追加し、messages_containerを更新
            for chunk in stream_response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    next_content = chunk['choices'][0].get('message', {}).get('content', '')
                    bot_message = {"role": "assistant", "content": next_content}
                    st.session_state["messages"].append(bot_message)

            update_messages_container(st.session_state["messages"])

        except Exception as e:
            st.error(f"APIリクエストでエラーが発生しました: {e}")
            st.write("エラー時のメッセージ履歴:")
            st.json(st.session_state["messages"])
            return

        st.session_state["user_input"] = ""

# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナの定義
messages_container = st.container()


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
    user_input = st.text_area("", key="user_input", height=100, placeholder="メッセージを入力してください。")
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