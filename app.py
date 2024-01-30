
import streamlit as st
import openai
import json

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    # st.secrets.AppSettings.chatbot_setting が文字列であることを確認
    initial_content = str(st.secrets.AppSettings.chatbot_setting)
    st.session_state["messages"] = [
        {"role": "system", "content": initial_content}
    ]

# その他のコード...


# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    # メッセージ履歴を制限（例：最新の5件に限定）
    if len(messages) > 5:
        st.session_state["messages"] = messages[-5:]
        messages = st.session_state["messages"]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=messages
        )

        bot_message = {"role": "assistant", "content": response["choices"][0]["message"]}
        messages.append(bot_message)

    except Exception as e:
        st.error(f"APIリクエストでエラーが発生しました: {e}")
        st.write("エラー時のメッセージ履歴:")
        st.json(messages)  # エラー時のメッセージ履歴を表示
        return

    st.session_state["user_input"] = ""  # 入力欄を消去


# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナ
messages_container = st.container()

if st.session_state.get("messages"):
    messages = st.session_state["messages"]

    for message in messages[1:]:
        speaker = "🙂"
        if message["role"] == "assistant":
            speaker = "🤖"
        
        content = message["content"]
        if not isinstance(content, str):
            content = str(content)

        # JSON形式の文字列をデコード
        try:
            decoded_content = json.loads(content)
            if "content" in decoded_content:
                content = decoded_content["content"]
        except json.JSONDecodeError:
            # JSON形式でない場合はそのまま使用
            pass
        
        messages_container.write(speaker + ": " + content)

# メッセージ入力
user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

# スクロール位置を最新のメッセージに自動調整
if st.session_state.get("messages"):
    st.markdown(
        f"<script>const elements = document.querySelectorAll('.element-container:not(.stButton)');"
        f"elements[elements.length - 1].scrollIntoView();</script>",
        unsafe_allow_html=True,
    )