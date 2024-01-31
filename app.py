import streamlit as st
import openai
import traceback
import json

# OpenAI APIキーの設定
try:
    openai.api_key = st.secrets["OpenAIAPI"]["openai_api_key"]
except Exception as e:
    st.error(f"OpenAI APIキーの設定に失敗しました: {e}")
    st.error(traceback.format_exc())  # スタックトレースの表示

st.title("QUICKFIT BOT")
st.write("Quick fitに関するQ&A AIBOT")

try:
    # メッセージ履歴の初期化と初期プロンプトの設定
    if "messages" not in st.session_state:
        initial_prompt = str(st.secrets["AppSettings"]["initial_prompt"])
        st.session_state["messages"] = [{"role": "system", "content": initial_prompt}]

    # チャットログを保存したセッション情報を初期化
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    user_msg = st.chat_input("ここにメッセージを入力")
    if user_msg:
        # 以前のチャットログを表示
        for chat in st.session_state.chat_log:
            with st.chat_message(chat["name"]):
                st.markdown(chat["msg"])

        # 最新のメッセージを表示
        with st.chat_message("user"):
            st.markdown(user_msg)

        # OpenAIからの応答を取得
        st.session_state["messages"].append({"role": "user", "content": user_msg})
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=st.session_state["messages"],
            stream=True
        )

        # アシスタントのメッセージを逐次表示
    assistant_msg = ""
    assistant_response_area = st.empty()

    # ストリーム処理の修正
    for message in response.iter_lines():
        if message:
            data = json.loads(message)
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    # メッセージを追加してUIに表示
                    assistant_msg += choice['message']['content']
                    assistant_response_area.markdown(assistant_msg)
                    # チャットログにアシスタントのメッセージを追加
                    st.session_state.chat_log.append({"name": "user", "msg": user_msg})
                    st.session_state.chat_log.append({"name": "assistant", "msg": assistant_msg})
                    if 'finish_reason' in choice and choice['finish_reason'] is not None:
                        break

except Exception as e:
    st.error(f"ストリーム処理中にエラーが発生しました: {e}")
    st.error(traceback.format_exc())
