
import streamlit as st
import openai

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting}
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

    bot_message = {"role": "assistant", "content": response["choices"][0]["message"]}
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去

# CSSスタイルを追加
st.markdown(
    """
    <style>
    .chat-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .chat-message {
        padding: 5px 10px;
        border-radius: 20px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
    }
    .user-message {
        background-color: #0078ff;
        color: white;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #e0e0e0;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナ
messages_container = st.container()

if st.session_state.get("messages"):
    messages = st.session_state["messages"]

    # メッセージをコンテナに表示
    with messages_container:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for message in messages[1:]:  # 直近のメッセージを下に表示
            if message["role"] == "user":
                st.markdown(f"<div class='chat-message user-message'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-message assistant-message'>{message['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# メッセージ入力
user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)
