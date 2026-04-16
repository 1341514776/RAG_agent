"""
    基于streamlit完成网页上传
    
    streamlit: 页面发生变化时，整个脚本会重新运行一次，所以需要注意状态的管理。
"""
import streamlit as st
from knowledge_base import KnowledgeBaseService

st.title("更新知识库")

upload_file = st.file_uploader("上传文件", type=["txt",], accept_multiple_files=False)

# SESSION_STATE是streamlit提供的一个全局字典对象，可以用来存储跨页面、跨组件的状态信息。当页面发生变化时，整个脚本会重新运行一次，但SESSION_STATE中的数据不会丢失，可以保持状态的连续性。
if "service" not in st.session_state:
    st.session_state.service = KnowledgeBaseService()

if upload_file is not None:
    print("上传文件：", upload_file)
    text = upload_file.getvalue().decode("utf-8")
    result = st.session_state.service.upload_by_str(text, upload_file.name)
    st.write(result)