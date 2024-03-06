import logging
from anthropic import Anthropic
import time
import streamlit as st

def response_claude(user_msg: str, past_messages: list, anthropic_api_key: str):
    anthropic = Anthropic(api_key=anthropic_api_key)

    # 過去のメッセージに現在のメッセージを追加
    past_messages = manage_past_messages(past_messages, user_msg, "")

    logging.info(f"Request to Anthropic API: {past_messages}")
    st.info(f"Request to Anthropic API: {past_messages}")  # Streamlitアプリケーションにログを表示

    try:
        # レスポンスを生成
        st.info("Generating response...")  # 処理開始のログを表示
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            messages=past_messages,
            max_tokens=1024,
        )
        response_text = response.content
        logging.info(f"Response from Anthropic API: {response_text}")
        st.info(f"Response from Anthropic API: {response_text}")  # Streamlitアプリケーションにログを表示
        return response_text
    except Exception as e:
        logging.error(f"Error occurred while making request to Anthropic API: {str(e)}")
        st.error(f"Error occurred while making request to Anthropic API: {str(e)}")  # エラーログを表示
        
        # エラーが発生した場合、ダミーの応答を返す
        error_response = "申し訳ありません。メッセージの処理中にエラーが発生しました。もう一度お試しください。"
        return error_response

def manage_past_messages(past_messages: list, new_user_message: str, new_assistant_message: str):
    # 新しいユーザーメッセージとアシスタントの応答を追加
    updated_messages = past_messages + [{"role": "user", "content": new_user_message}]

    # アシスタントの応答が生成された場合、それを追加
    if new_assistant_message:
        updated_messages.append({"role": "assistant", "content": new_assistant_message})

    # 連続した "user" ロールのメッセージがある場合、古いメッセージを削除
    while len(updated_messages) >= 3 and updated_messages[-1]["role"] == "user" and updated_messages[-2]["role"] == "user":
        updated_messages.pop(0)

    return updated_messages
