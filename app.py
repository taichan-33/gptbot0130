import streamlit as st
import openai
import json

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# キャッシュされたチャット関数
@st.cache(allow_output_mutation=True)
def cached_chat(messages):
    completion = openai.ChatCompletion.create(
        model='gpt-4-0125-preview',
        messages=messages,
        stream=True,
    )
    return completion

# メッセージ履歴の初期化
if "messages" not in st.session_state:
    initial_content = str(st.secrets.AppSettings.chatbot_setting)
    st.session_state["messages"] = [{"role": "system", "content": initial_content}]

# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナ
messages_container = st.container()
user_input = st.text_area("メッセージを入力", key="user_input", height=100, placeholder="メッセージを入力してください。")
send_button = st.button("➤", key="send_button")

def stream_write(completion, key=None):
    result_area = st.empty()
    text = ''
    for chunk in completion:
        # Check if the necessary keys are in the chunk
        if 'choices' in chunk and len(chunk['choices']) > 0:
            message = chunk['choices'][0]['message']
            if 'content' in message:
                next_content = message['content']
            else:
                next_content = message  # or some default value or error handling
        else:
            next_content = "エラー: 予期しないレスポンス形式"
        
        text += next_content
        if "。" in next_content:
            text += "\n"
        result_area.write(text, key=key)
    return text


# 送信ボタンが押されたらメッセージを処理
if send_button and user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    completion = cached_chat(st.session_state["messages"])
    response_text = stream_write(completion)
    st.session_state["messages"].append({"role": "assistant", "content": response_text})
    st.session_state["user_input"] = ""

# メッセージの表示
if st.session_state.get("messages"):
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        speaker = "🙂YOU" if message["role"] == "user" else "🤖BOT"
        messages_container.write(speaker + ": " + message["content"])


# カスタムCSSを追加
st.markdown("""
    <style>
        .stTextArea > div > div > textarea {
            height: 50px; /* テキストボックスの高さ調整 */
            color: blue; /* テキストボックスのテキスト色 */
        }
        .stButton > button {
            height: 50px; /* ボタンの高さ調整 */
            color: blue; /* ボタンのテキスト色 */
            background-color: lightgray; /* ボタンの背景色 */
            vertical-align: low; /* ボタンの垂直方向の配置を中央に調整 */
        }
    </style>
    """, unsafe_allow_html=True)

# Ctrl+Enterで送信するためのJavaScript
st.markdown("""
    <script>
        document.addEventListener("keydown", function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                document.querySelector('.stButton > button').click();
            }
        });
    </script>
    """, unsafe_allow_html=True)

# スクロール位置を最新のメッセージに自動調整するためのスクリプト
st.markdown(
    f"<script>const elements = document.querySelectorAll('.element-container:not(.stButton)');"
    f"elements[elements.length - 1].scrollIntoView();</script>",
    unsafe_allow_html=True,
)
