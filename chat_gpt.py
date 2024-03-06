import openai

def response_chatgpt(user_msg: str, past_messages: list):
    """ChatGPTのレスポンスを取得

    Args:
        user_msg (str): ユーザーメッセージ。
        past_messages (list): 過去のメッセージリスト（ユーザーとアシスタントの両方）。
    """
    # 過去のメッセージに現在のメッセージを追加
    messages_to_send = past_messages + [{"role": "user", "content": user_msg}]
    # ChatGPTにメッセージを送信し、レスポンスを取得
    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=messages_to_send,
        stream=True,
    )
    return response
