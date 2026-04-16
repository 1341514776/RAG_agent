
md5_path = './md5.text' #md5文件路径

# chroma配置
collection_name = 'rag'  # 向量数据库集合名称
persist_directory = './chroma_db'  # 向量数据库持久化目录
# 文本分割配置
chunk_size = 100  # 分块大小
chunk_overlap = 50  # 分块重叠大小,阿松大
separators = ['\n\n', '\n', '.', '!', '?', ',', ' ', '', '，', '。']  # 分割符列表
max_split_length = 100  # 文本分割最大长度

# 向量数据库检索配置
top_k = 2  # 向量数据库检索返回的相关文档数量


#模型
embedding_name = "text-embedding-v4" #向量化模型名称
chat_model_name = "qwen-plus" #聊天模型名称


session_config = {
    "configurable": {
        "session_id": "user_001"
    }
}