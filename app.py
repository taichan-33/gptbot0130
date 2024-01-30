
import streamlit as st
import openai

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "あなたは優秀なアシスタントAIです。"}
        ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去


# ユーザーインターフェイスの構築
st.title("My AI Assistant")
st.write("ChatGPT APIを使ったチャットボットです。")

# メッセージ表示用のコンテナ
messages_container = st.container()

if st.session_state.get("messages"):
    messages = st.session_state["messages"]

    # メッセージをコンテナに表示
    for message in messages[1:]:  # 直近のメッセージを下に表示
        speaker = "🙂"
        if message["role"] == "assistant":
            speaker = "🤖"
        messages_container.write(speaker + ": " + message["content"])

# メッセージ入力
user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

# スクロール位置を最新のメッセージに自動調整
if st.session_state.get("messages"):
    st.markdown(
        f"<script>const elements = document.querySelectorAll('.element-container:not(.stButton)');"
        f"elements[elements.length - 1].scrollIntoView();</script>",
        unsafe_allow_html=True,
    )
