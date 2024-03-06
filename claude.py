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
                # We assume the first complete sentence ends with a period, question mark, or exclamation mark.
                if "." in text or "?" in text or "!" in text:
                    # Find the end of the first sentence and break
                    end_of_sentence = min([text.find(char) for char in '.?!' if char in text])
                    response_text += text[:end_of_sentence + 1]
                    break
                else:
                    response_text += text

        # Strip any extra whitespace from the response and update the placeholder
        response_text = response_text.strip()
        response_placeholder.markdown(f"> {response_text}")

        return response_text
    
    except Exception as e:
        logging.error(f"Error occurred while making request to Anthropic API: {str(e)}")
        
        # Return a dummy response in case of an error
        error_response = "申し訳ありません。メッセージの処理中にエラーが発生しました。もう一度お試しください。"
        return error_response


def manage_past_messages(past_messages: list, new_user_message: str, new_assistant_message: str):
    # Add the new user message and assistant's response
    updated_messages = [msg for msg in past_messages if msg["role"] != "system" and msg["content"].strip()]
    
    if new_user_message.strip():
        if not updated_messages or updated_messages[-1]["role"] == "assistant":
            updated_messages.append({"role": "user", "content": new_user_message})
        else:
            updated_messages[-1]["content"] += "\n" + new_user_message
    
    if new_assistant_message.strip():
        updated_messages.append({"role": "assistant", "content": new_assistant_message})
    
    return updated_messages
