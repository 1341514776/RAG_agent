"""
知识库

"""

import os
import config  
import hashlib
from datetime import datetime, timedelta 
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

os.environ["DASHSCOPE_API_KEY"] = "sk-fbfd1d070d274910b40189a2724f001d" # 替换为你的OpenAI API Key
def check_md5(md5_str: str) -> bool:
    if not os.path.exists(config.md5_path):
        open(config.md5_path, 'w', encoding='utf-8').close()  # 创建空文件
    else:
        for line in open(config.md5_path, 'r', encoding='utf-8'):
            line = line.strip()
            if line == md5_str:
                return True
    return False


def save_md5(md5_str: str):
    with open(config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str + '\n')
    


def get_str_md5(input_str: str, encoding: str = 'utf-8') -> str:
    str_bytes = input_str.encode(encoding)
    md5_obj = hashlib.md5() # 创建MD5对象
    md5_obj.update(str_bytes) # 更新MD5对象
    return md5_obj.hexdigest() # 获取MD5值


class KnowledgeBaseService(object):
    def __init__(self):
        #如果文件夹不存在 则创建
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
                collection_name=config.collection_name, #向量数据库集合名称
                persist_directory=config.persist_directory, #向量数据库持久化目录
                embedding_function=DashScopeEmbeddings(model=config.embedding_name) #向量化模型
        )  # 向量数据库
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, #分块大小
            chunk_overlap=config.chunk_overlap, #分块重叠大小
            separators=config.separators, #分割符列表
            length_function=len #长度函数
        )  # 文本分割器

    def upload_by_str(self, data, fileName):
        """上传字符串数据"""
        
        md5_hex = get_str_md5(data)
        if check_md5(md5_hex):
            print(f"{fileName} 已经上传过了，跳过上传")
            return f"{fileName} 已经上传过了，跳过上传"
        #文本分割 
        if len(data) > config.max_split_length:
            knowledge_chunks = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]
        #向量化并存储
        metadata = {
            "file_name": fileName,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.chroma.add_texts(knowledge_chunks, metadatas=[metadata for _ in knowledge_chunks])
        #保存md5
        save_md5(md5_hex)
        print(f"{fileName} 上传成功！")
        return f"{fileName} 上传成功！"
         

# if __name__ == '__main__':
#     knowledge = KnowledgeBaseService()
#     data = "这是一个测试文本，用于测试知识库的上传功能。"
#     knowledge.upload_by_str(data, "test.txt")