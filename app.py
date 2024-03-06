import os
import openai
import streamlit as st
from anthropic import Anthropic
import pandas as pd
import time
import anthropic
import traceback


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

# OpenAIクライアントの初期化
client = openai.ChatCompletion()


class ClaudeLlm:
    def __init__(self, anthropic, user_msg):
        self.anthropic = anthropic
        self.user_msg = user_msg

    def generate_responses(self, model):
        start_time = time.time()
        input_tokens = 0
        output_tokens = 0

        try:
            response = self.anthropic.completions.create(
                model=model,
                prompt=self.user_msg,
                stop_sequences=[],
                max_tokens_to_sample=4096,
                stream=True,
            )

            response_buffer = ""
            for chunk in response:
                if isinstance(chunk, dict) and "completion" in chunk:
                    response_buffer += chunk["completion"]

            return response_buffer

        except Exception as e:
            logging.error(
                f"Error occurred while making request to Anthropic API: {str(e)}"
            )
            raise


def response_chatgpt(user_msg: str, past_messages: list):
    """ChatGPTのレスポンスを取得

    Args:
        user_msg (str): ユーザーメッセージ。
        past_messages (list): 過去のメッセージリスト（ユーザーとアシスタントの両方）。
    """
    # 過去のメッセージに現在のメッセージを追加
    messages_to_send = past_messages + [{"role": "user", "content": user_msg}]
    # ChatGPTにメッセージを送信し、レスポンスを取得
    response = client.create(
        model="gpt-4-0125-preview",
        messages=messages_to_send,
        stream=True,
    )
    return response


import logging


def response_claude(user_msg: str, past_messages: list):
    anthropic = Anthropic(api_key=anthropic_api_key)

    system_prompt = next(
        (msg["content"] for msg in past_messages if msg["role"] == "system"), None
    )

    filtered_messages = [
        msg for msg in past_messages if msg["role"] in ["user", "assistant"]
    ]

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    for message in filtered_messages:
        if message["content"].strip():
            messages.append(message)

    messages.append({"role": "user", "content": user_msg})

    logging.info(f"Request to Anthropic API: {messages}")

    try:
        response = client.completions.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.0,
            prompt=messages,
        )

        logging.info(f"Response from Anthropic API: {response}")
        return response

    except Exception as e:
        error_message = (
            f"Error occurred while making request to Anthropic API: {str(e)}"
        )
        error_traceback = traceback.format_exc()
        logging.error(error_message)
        logging.error(f"Traceback: {error_traceback}")
        st.error(error_message)
        raise


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
        response = response_claude(user_msg, st.session_state["messages"])

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
