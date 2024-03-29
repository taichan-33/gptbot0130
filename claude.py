import logging
from anthropic import Anthropic
import time
import streamlit as st

def response_claude(user_msg: str, past_messages: list, anthropic_api_key: str):
   anthropic = Anthropic(api_key=anthropic_api_key)
   
   # 過去のメッセージに現在のメッセージを追加
   past_messages = manage_past_messages(past_messages, user_msg, "")
   logging.info(f"Request to Anthropic API: {past_messages}")
   
   try:
       # ストリーム出力用のプレースホルダーを作成
       response_placeholder = st.empty()
       
       # レスポンスを生成
       with anthropic.messages.stream(
           model="claude-3-opus-20240229",
           messages=past_messages,
           max_tokens=1024,
       ) as stream:
           # レスポンスをストリーム出力
           response_text = ""
           for text in stream.text_stream:
               response_text += text
               response_placeholder.markdown(response_text)
               logging.info(f"Streamed response: {text}")  # ストリームされたレスポンスをログ出力
       
       logging.info(f"Final response: {response_text}")  # 最終的なレスポンスをログ出力
       return response_text
   except Exception as e:
       logging.error(f"Error occurred while making request to Anthropic API: {str(e)}")
       # エラーが発生した場合、ダミーの応答を返す
       error_response = "申し訳ありません。メッセージの処理中にエラーが発生しました。もう一度お試しください。"
       return error_response

def manage_past_messages(past_messages: list, new_user_message: str, new_assistant_message: str):
   # 新しいユーザーメッセージとアシスタントの応答を追加
   updated_messages = [msg for msg in past_messages if msg["role"] != "system" and msg["content"].strip()]
   
   if new_user_message.strip():
       if not updated_messages or updated_messages[-1]["role"] == "assistant":
           updated_messages.append({"role": "user", "content": new_user_message})
       else:
           updated_messages[-1]["content"] += "\n" + new_user_message
   
   # アシスタントの応答が空文字列でない場合のみ追加
   if new_assistant_message.strip():
       updated_messages.append({"role": "assistant", "content": new_assistant_message})
   
   return updated_messages
