import logging
from anthropic import Anthropic
import streamlit as st

def response_claude(user_msg: str, past_messages: list, anthropic_api_key: str):
    anthropic = Anthropic(api_key=anthropic_api_key)
    
    # Add the current message to the past messages
    past_messages = manage_past_messages(past_messages, user_msg, "")
    
    logging.info(f"Request to Anthropic API: {past_messages}")
    
    try:
        # Create a placeholder for the stream output
        response_placeholder = st.empty()
        
        # Generate the response
        with anthropic.messages.stream(
            model="claude-3-opus-20240229",
            messages=past_messages,
            max_tokens=1024,
        ) as stream:
            # Stream the response
            response_text = ""
            for text in stream.text_stream:
                response_text += text
                # Ensure only the text up to the first sentence-ending punctuation is included
                if any(punct in text for punct in [".", "?", "!"]):
                    end_index = min((text + response_text).find(punct) for punct in [".", "?", "!"] if punct in text)
                    response_text = (text + response_text)[:end_index + 1]
                    response_placeholder.markdown(response_text)
                    break
        
        # Update the placeholder with only the first complete response
        response_placeholder.markdown(response_text.strip())
        
        return response_text.strip()
    
    except Exception as e:
        logging.error(f"Error occurred while making request to Anthropic API: {str(e)}")
        
        # Return a dummy response in case of an error
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
    
    # アシスタントの応答が生成された場合、それを追加
    if new_assistant_message.strip():
        updated_messages.append({"role": "assistant", "content": new_assistant_message})
    
    return updated_messages
