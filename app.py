# StreamlitとOpenAIライブラリをインポート
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

# ユーザーインターフェイスの構築
st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")



# スクロールを最下部に移動するJavaScript
st.markdown(
    """
    <script>
    // スクロールをページの最下部に移動する関数
    function scrollToBottom() {
        window.scrollTo(0, document.body.scrollHeight);
    }

    // 100ミリ秒後にスクロールを実行
    setTimeout(scrollToBottom, 100);
    </script>
    """,
    unsafe_allow_html=True
)


# ページ最下部への自動スクロールを行うスクリプト
def scroll_to_bottom():
    st.markdown(
        """
        <script>
        window.scrollTo(0, document.body.scrollHeight);
        </script>
        """,
        unsafe_allow_html=True
    )

# 会話履歴を表示する関数
def display_messages(messages):
    for message in messages:
        if message["role"] == "system":
            continue
        speaker = "🙂YOU: " if message["role"] == "user" else ""
        messages_container.markdown(f"{speaker}{message['content']}\n")  # 空白行を追加

# チャットボットとやりとりする関数
def communicate():
    if "user_input" in st.session_state and st.session_state["user_input"]:
        messages = st.session_state["messages"]

        user_message = {"role": "user", "content": st.session_state["user_input"]}
        messages.append(user_message)

        # ストリームレスポンス全体の内容を格納する変数
        full_stream_content = ""

        try:
            # ストリームレスポンスの取得
            stream_response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                messages=messages,
                stream=True
            )

            # ストリームレスポンスをリアルタイムで表示
            for chunk in stream_response:
                next_content = chunk['choices'][0]['delta'].get('content', '')
                full_stream_content += next_content

            # ストリームが完了したら、最終的なメッセージをmessagesに追加して表示
            bot_message = {"role": "assistant", "content": full_stream_content}
            messages.append(bot_message)

        except Exception as e:
            st.error(f"APIリクエストでエラーが発生しました: {e}")

        # 会話履歴を更新
        display_messages(st.session_state["messages"])

        # 入力フィールドをクリア
        st.session_state["user_input"] = ""

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

# メッセージ表示用のコンテナ
messages_container = st.container()
# ストリームレスポンス用のプレースホルダーをメッセージ表示コンテナ内に作成
stream_placeholder = messages_container.empty()

# メッセージ入力（改行可能）と送信ボタンを横並びに配置
col1, col2 = st.columns([5, 2], gap="small")
with col1:
    user_input = st.text_area("メッセージを入力", key="user_input", height=100, placeholder="メッセージを入力してください。")
with col2:
    send_button = st.button("➤", key="send_button", on_click=communicate)

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
