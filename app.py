import streamlit as st
from streamlit_chat import message
import openai

# OpenAI APIキーの設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# タイトル設定
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ履歴の初期化と初期プロンプトの設定
if "messages" not in st.session_state:
    initial_prompt = str(st.secrets.AppSettings.initial_prompt)
    st.session_state["messages"] = [
        {"role": "system", "content": initial_prompt}
    ]

# ユーザーの入力を取得
with st.container():
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Your message here:", placeholder="Ask your question here", key='input')
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        # ユーザーメッセージを履歴に追加
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # OpenAIから応答を取得
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=st.session_state["messages"]
        )

        # ボットの応答を履歴に追加
        full_response = response["choices"][0]["message"]["content"]
        st.session_state["messages"].append({"role": "assistant", "content": full_response})

# ユーザーとチャットボットのメッセージ表示
with st.container():
    for message_info in st.session_state["messages"]:
        if message_info["role"] == "user":
            message(message_info["content"], is_user=True, avatar_style="big-smile")
        elif message_info["role"] == "assistant":
            message(message_info["content"], avatar_style="thumbs")
