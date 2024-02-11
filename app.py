import openai
import streamlit as st
from PIL import Image
import io
import base64

# OpenAI APIキーの設定
openai.api_key = st.secrets["OpenAIAPI"]["openai_api_key"]

st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

# Streamlit UIの一部を非表示にするCSS
HIDE_ST_STYLE = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                </style>
"""

st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)

# 定数定義
USER_NAME = "user"
ASSISTANT_NAME = "assistant"

# OpenAIクライアントの初期化
client = openai.ChatCompletion()

def response_chatgpt(user_msg: str, past_messages: list, img_str: str = ""):
    """ChatGPTのレスポンスを取得

    Args:
        user_msg (str): ユーザーメッセージ。
        past_messages (list): 過去のメッセージリスト（ユーザーとアシスタントの両方）。
        img_str (str): Base64エンコードされた画像データ。
    """
    messages_to_send = past_messages
    if img_str:
        # 画像データがある場合、それをメッセージに追加
        messages_to_send += [{"role": "user", "content": {"type": "image_base64", "image_base64": img_str}}]
    if user_msg:
        # ユーザーメッセージを追加
        messages_to_send += [{"role": "user", "content": user_msg}]
    
    # ChatGPTにメッセージを送信し、レスポンスを取得
    response = client.create(
        model="gpt-4-0125-preview",
        messages=messages_to_send,
        stream=True,
    )
    return response

# メッセージ履歴の初期化と初期プロンプトの設定
if "messages" not in st.session_state:
    initial_prompt = str(st.secrets["AppSettings"]["initial_prompt"])
    st.session_state["messages"] = [{"role": "system", "content": initial_prompt}]

# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# 画像アップロード機能
uploaded_file = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])
img_str = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# テキスト入力機能
user_msg = st.text_input("ここにメッセージを入力（または画像の質問をします）")

if user_msg or img_str:
    # チャットログの表示とアップデート
    response = response_chatgpt(user_msg, st.session_state["messages"], img_str)
    assistant_msg = ""
    for chunk in response:
        if chunk.choices[0].finish_reason is not None:
            break
        assistant_msg += chunk.choices[0].delta.content
    
    st.session_state["messages"].append({"role": "user", "content": user_msg})
    st.session_state["messages"].append({"role": "assistant", "content": assistant_msg})
    st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})

    # アシスタントのメッセージを表示
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["name"]):
            st.write(chat["msg"])
