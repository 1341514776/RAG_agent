import time

import streamlit as st
import config

from rag import RagService

st.title("Question Answering")  # 标题

st.divider()  # 分割线

if 'message' not in st.session_state:
    st.session_state['message'] = []

if 'rag' not in st.session_state:
    st.session_state['rag'] = RagService()

for message in st.session_state['message']:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt is not None:
    st.chat_message("user").write(prompt)  # 显示用户输入
    st.session_state['message'].append({"role": "user", "content": prompt})  # 将用户输入添加到消息列表中


    def collect_stream(stream, list):
        for item in stream:
            list.append(item)
            yield stream


    txt_list = []
    with st.spinner('思考中....'):
        res_stream = st.session_state['rag'].chain.stream({'question': prompt}, config.session_config)

        st.chat_message('assistant').write_stream(collect_stream(res_stream, txt_list))  # 显示模型回答
        st.session_state['message'].append({"role": "assistant", "content": txt_list})
