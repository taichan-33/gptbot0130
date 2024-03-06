import os
import openai
import streamlit as st
from chat_gpt import response_chatgpt
from claude import response_claude
import pandas as pd
import time

# OpenAI APIキーの設定
openai.api_key = st.secrets["OpenAIAPI"]["openai_api_key"]

# Anthropic APIキーの設定
anthropic_api_key = st.secrets["AnthropicAPI"]["anthropic_api_key"]

st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

HIDE_ST_STYLE = """
<style>
div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
div[data-testid="stDecoration"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
</style>
"""

st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)

# 定数定義
USER_NAME = "user"
ASSISTANT_NAME = "assistant"

# サイドバーの追加
model = st.sidebar.selectbox("Select Model", ["chatgpt", "claude3 opus"])

# メッセージ履歴の初期化と初期プロンプトの設定
if "messages" not in st.session_state:
    initial_prompt = str(st.secrets["AppSettings"]["initial_prompt"])
    st.session_state["messages"] = [{"role": "system", "content": initial_prompt}]

# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

user_msg = st.chat_input("ここにメッセージを入力")

if user_msg:
    # 以前のチャットログを表示
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["name"]):
            st.write(chat["msg"])

    # 最新のメッセージを表示
    with st.chat_message(USER_NAME):
        st.write(user_msg)

    # モデルに応じてレスポンスを取得
    if model == "chatgpt":
        response = response_chatgpt(user_msg, st.session_state["messages"])
    elif model == "claude3 opus":
        response = response_claude(user_msg, st.session_state["messages"], anthropic_api_key)

    # アシスタントのメッセージを表示
    with st.chat_message(ASSISTANT_NAME):
        assistant_msg = ""
        assistant_response_area = st.empty()
        for chunk in response:
            if model == "chatgpt":
                if chunk.choices[0].finish_reason is not None:
                    break
                assistant_msg += chunk.choices[0].delta.content
            elif model == "claude3 opus":
                if isinstance(chunk, str):
                    assistant_msg += chunk
            assistant_response_area.write(assistant_msg)

    # セッションにチャットログを追加
    st.session_state["messages"].append({"role": "user", "content": user_msg})
    st.session_state["messages"].append({"role": "assistant", "content": assistant_msg})
    st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})
