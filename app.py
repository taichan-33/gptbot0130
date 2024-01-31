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
        st.session_state["chat_log"] = []

    user_msg = st.chat_input("ここにメッセージを入力")
    if user_msg:
        # ユーザーのメッセージをセッションのチャットログに追加
        st.session_state.chat_log.append({"name": "user", "msg": user_msg})

        # 以前のチャットログを表示
        for chat in st.session_state.chat_log:
            with st.chat_message(chat["name"]):
                st.markdown(chat["msg"])

        # OpenAIからの応答を取得
        st.session_state["messages"].append({"role": "user", "content": user_msg})
        response_gen = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=st.session_state["messages"],
            stream=True
        )

        # アシスタントのメッセージを逐次表示
        assistant_msg = ""
        assistant_response_area = st.empty()

        # ストリーム処理
        try:
            for response in response_gen:
                if 'choices' in response and len(response['choices']) > 0:
                    choice = response['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        assistant_msg += choice['message']['content']
                        assistant_response_area.markdown(assistant_msg)
                        if choice.get('finish_reason') is not None:
                            # チャットログにアシスタントのメッセージを追加して表示
                            st.session_state.chat_log.append({"name": "assistant", "msg": assistant_msg})
                            break
        except Exception as inner_e:
            st.error(f"ストリームの読み込み中にエラーが発生しました: {inner_e}")
            st.error(traceback.format_exc())

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    st.error(traceback.format_exc())
