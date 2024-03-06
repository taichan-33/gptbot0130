import logging
from anthropic import Anthropic
import time

def response_claude(user_msg: str, past_messages: list, anthropic_api_key: str):
    anthropic = Anthropic(api_key=anthropic_api_key)

    # ユーザーとアシスタントのメッセージのみを残す
    filtered_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in past_messages
        if msg["role"] in ["user", "assistant"]
    ]

    # 過去のメッセージに現在のメッセージを追加
    messages = filtered_messages + [{"role": "user", "content": user_msg}]

    logging.info(f"Request to Anthropic API: {messages}")

    try:
        # レスポンスを生成
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            messages=messages,
            max_tokens_to_sample=1024,
            stream=True,
        )

        response_buffer = ""
        for chunk in response:
            if isinstance(chunk, dict) and "text" in chunk:
                response_buffer += chunk["text"]

        logging.info(f"Response from Anthropic API: {response_buffer}")
        return response_buffer

    except Exception as e:
        logging.error(f"Error occurred while making request to Anthropic API: {str(e)}")
        raise
