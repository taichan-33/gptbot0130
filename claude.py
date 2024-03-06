import logging
from anthropic import Anthropic
import time

class ClaudeLlm:
    def __init__(self, anthropic, user_msg):
        self.anthropic = anthropic
        self.user_msg = user_msg

    def generate_responses(self, model):
        start_time = time.time()
        input_tokens = 0
        output_tokens = 0

        try:
            # user_msgがリストの場合、適切な形式に変換する
            if isinstance(self.user_msg, list):
                prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.user_msg])
            else:
                prompt = self.user_msg

            response = self.anthropic.completions.create(
                model=model,
                prompt=prompt,
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


def response_claude(user_msg: str, past_messages: list, anthropic_api_key: str):
    anthropic = Anthropic(api_key=anthropic_api_key)

    # システムプロンプトを取り出す
    system_prompt = next(
        (msg["content"] for msg in past_messages if msg["role"] == "system"), None
    )

    # ユーザーとアシスタントのメッセージのみを残す
    filtered_messages = [
        msg for msg in past_messages if msg["role"] in ["user", "assistant"]
    ]

    # 過去のメッセージに現在のメッセージを追加
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    for message in filtered_messages:
        if message["content"].strip():  # 空でないコンテンツのみを追加
            messages.append(message)

    messages.append({"role": "user", "content": user_msg})

    logging.info(f"Request to Anthropic API: {messages}")

    try:
        # ClaudeLlmクラスのインスタンスを作成
        claude = ClaudeLlm(anthropic, messages)

        # レスポンスを生成
        response_buffer = ""
        for chunk in claude.generate_responses("claude-3-opus-20240229"):
            response_buffer += chunk

        logging.info(f"Response from Anthropic API: {response_buffer}")
        return response_buffer

    except Exception as e:
        logging.error(f"Error occurred while making request to Anthropic API: {str(e)}")
        raise
