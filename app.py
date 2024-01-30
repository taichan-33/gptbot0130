import streamlit as st
import openai
import json

# StreamlitのカスタムCSSを設定
st.markdown("""
    <style>
        /* タイトルのスタイル調整 */
        .title {
            color: white;
            font-size: 1.75em; /* タイトルのサイズを調整 */
        }
        .title span {
            color: red;
        }
        .title span:nth-of-type(4) {
            color: blue;
        }

        /* ダークモードの背景とテキストカラー */
        body, .stTextInput, .stTextArea, .stSelectbox, .stMultiSelect, .stRadio, .stCheckbox, .stSlider, .css-9e6fub {
            color: white !important;
            background-color: #121212 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    initial_content = str(st.secrets.AppSettings.chatbot_setting)
    st.session_state["messages"] = [
        {"role": "system", "content": initial_content}
    ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=messages
        )

        bot_message_content = response["choices"][0]["message"]["content"] if "content" in response["choices"][0]["message"] else response["choices"][0]["message"]
        bot_message = {"role": "assistant", "content": bot_message_content}
        messages.append(bot_message)

    except Exception as e:
        st.error(f"APIリクエストでエラーが発生しました: {e}")
        st.write("エラー時のメッセージ履歴:")
        st.json(messages)  # エラー時のメッセージ履歴を表示
        return

    st.session_state["user_input"] = ""  # 入力欄を消去

# ユーザーインターフェイスの構築
st.markdown('<p class="title">QU<span>I</span>CKF<span>I</span>T BOT</p>', unsafe_allow_html=True)
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナ
messages_container = st.container()

if st.session_state.get("messages"):
    messages = st.session_state["messages"]

    for message in messages:
        # システムメッセージはスキップする
        if message["role"] == "system":
            continue

        speaker = "🙂"
        if message["role"] == "assistant":
            speaker = "🤖"

        content = message["content"]
        if not isinstance(content, str):
            content = str(content)

        messages_container.write(speaker + ": " + content)

# メッセージ入力
user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

# スクロール位置を最新のメッセージに自動調整
st.markdown(
    f"<script>const elements = document.querySelectorAll('.element-container:not(.stButton)');"
    f"elements[elements.length - 1].scrollIntoView();</script>",
    unsafe_allow_html=True,
)
