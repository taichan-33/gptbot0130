import logging
from anthropic import Anthropic
import time

def response_claude(user_msg: str, past_messages: list, anthropic_api_key: str):
    anthropic = Anthropic(api_key=anthropic_api_key)

    # ユーザーとアシスタントのメッセージのみを残す
    filtered_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in past_messages
        if msg["role"] in ["user", "assistant"] and msg["content"].strip()
    ]

    # 過去のメッセージに現在のメッセージを追加
    messages = filtered_messages + [{"role": "user", "content": user_msg}]

    logging.info(f"Request to Anthropic API: {messages}")

    try:
        # レスポンスを生成
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            messages=messages,
            max_tokens=1024,
        )
        response_text = response.content
        logging.info(f"Response from Anthropic API: {response_text}")
        return response_text
    except Exception as e:
        logging.error(f"Error occurred while making request to Anthropic API: {str(e)}")
        
        # エラーが発生した場合、ダミーの応答を返す
        error_response = "申し訳ありません。メッセージの処理中にエラーが発生しました。もう一度お試しください。"
        return error_response

def manage_past_messages(past_messages: list, new_user_message: str, new_assistant_message: str):
    # 新しいユーザーメッセージを追加
    past_messages.append({"role": "user", "content": new_user_message})

    # アシスタントの応答が生成された場合、それを追加
    if new_assistant_message:
        past_messages.append({"role": "assistant", "content": new_assistant_message})
    else:
        # アシスタントの応答が生成されなかった場合、ダミーの応答を追加
        past_messages.append({"role": "assistant", "content": "申し訳ありません。メッセージの処理中にエラーが発生しました。もう一度お試しください。"})

    # 連続した "user" ロールのメッセージがある場合、古いメッセージを削除
    while len(past_messages) >= 3 and past_messages[-1]["role"] == "user" and past_messages[-2]["role"] == "user":
        past_messages.pop(0)

    return past_messages
