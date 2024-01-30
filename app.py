import streamlit as st
import openai
import json


# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    initial_content = str(st.secrets.AppSettings.chatbot_setting)
    st.session_state["messages"] = [
        {"role": "system", "content": initial_content}
    ]

# チャットボットとやりとりする関数
def communicate():
    if st.session_state["user_input"]:  # 入力が空でないことを確認
        user_message = {"role": "user", "content": st.session_state["user_input"]}
        st.session_state["messages"].append(user_message)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                messages=st.session_state["messages"]
            )

            bot_message_content = response["choices"][0]["message"]["content"]
            bot_message = {"role": "assistant", "content": bot_message_content}
            st.session_state["messages"].append(bot_message)

        except Exception as e:
            st.error(f"APIリクエストでエラーが発生しました: {e}")
            st.write("エラー時のメッセージ履歴:")
            st.json(st.session_state["messages"])  # エラー時のメッセージ履歴を表示

        st.session_state["user_input"] = ""  # 入力欄を消去

# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナ
messages_container = st.container()
with messages_container:
    for message in reversed(st.session_state["messages"]):
        if message["role"] == "system":
            continue
        speaker = "🙂" if message["role"] == "user" else "🤖"
        content = message["content"]
        st.text_area("", value=content, disabled=True, height=70, key=f"msg_{message}")

# メッセージ入力と送信ボタン
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)
with col2:
    st.button("送信", on_click=communicate, args=(user_input,))

# 最新のメッセージに自動スクロールするJavaScript
st.markdown("""
    <script>
        const messagesContainer = document.querySelector('.element-container:last-child');
        if(messagesContainer) {
            messagesContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    </script>
""", unsafe_allow_html=True)