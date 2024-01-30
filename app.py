import streamlit as st
import openai
import json
from uuid import uuid4  # uuidモジュールからuuid4をインポート

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets["OpenAIAPI"]["openai_api_key"]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def stream_write(chunks, key=None):
    result_area = st.empty()
    text = ''
    for chunk in chunks:
        next_content = chunk['choices'][0]['delta'].get('content', '')
        text += next_content
        if "。" in next_content:
            text += "\n"
        result_area.write(text, key=key)
    return text

# @st.cache_data() デコレータを削除して、キャッシュを使用しない設定に変更
def cached_chat(messages):
    try:
        completion = openai.ChatCompletion.create(
            model='gpt-4-0125-preview',
            messages=messages,
            stream=True
        )
        return list(completion)
    except Exception as e:
        st.error("APIリクエストエラー: " + str(e))
        return []


# メッセージ履歴の初期化
if "messages" not in st.session_state:
    initial_content = str(st.secrets["AppSettings"]["chatbot_setting"])
    st.session_state["messages"] = [{"role": "system", "content": initial_content}]

# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# メッセージ表示用のコンテナ
messages_container = st.container()

# メッセージの表示
if st.session_state.get("messages"):
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        speaker = "🙂YOU" if message["role"] == "user" else "🤖BOT"
        messages_container.write(speaker + ": " + message["content"])

# ユーザー入力テキストボックスの前に、セッション状態でuser_inputを管理
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ユーザー入力テキストボックスの定義
# 'user_input_text' セッション状態のキーを使用
if "user_input_text" not in st.session_state:
    st.session_state.user_input_text = ""
user_input = st.text_area("メッセージ入力", key="user_input", height=100, placeholder="メッセージを入力してください。", value=st.session_state.user_input_text)  # テキストエリアに"メッセージ入力"というラベルを設定


# 送信ボタンの定義と無効化の実装
send_button = st.button("➤", key="send_button", disabled=st.session_state.get("is_sending", False))

if send_button and user_input:
    st.session_state["is_sending"] = True
    st.experimental_rerun() # ボタンを無効化するためにスクリプトを再実行

    # ユーザーのメッセージをセッション状態に追加
    st.session_state["messages"].append({"role": "user", "content": user_input})
    # チャット応答を直接生成し表示
    completion = cached_chat(st.session_state["messages"])
    if completion is not None:
        response_text = stream_write(completion)
        st.session_state["messages"].append({"role": "assistant", "content": response_text})
    # テキストエリアの値をクリアする
    st.session_state.user_input_text = ""

    st.session_state["is_sending"] = False
    st.experimental_rerun() # ボタンを再度有効化するためにスクリプトを再実行

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
