import streamlit as st
import openai

# OpenAI APIキーの設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# タイトル設定
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ履歴の初期化と初期プロンプトの設定
if "messages" not in st.session_state:
    initial_prompt = str(st.secrets.AppSettings.initial_prompt)
    st.session_state["messages"] = [{"role": "system", "content": initial_prompt}]

# デフォルトモデルの設定
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-0125-preview"

# ユーザーの入力を取得
prompt = st.chat_input("Your message here:")
if prompt:
    # ユーザーメッセージを履歴に追加
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAIから応答を取得
    response = openai.ChatCompletion.create(
        model=st.session_state["openai_model"],
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True
    )

    # ボットの応答を表示
    full_response = ""
    for part in response:
        full_response += part['choices'][0]['delta'].get('content', '')
    with st.chat_message("assistant"):
        st.markdown(full_response)

    # 応答を履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": full_response})
