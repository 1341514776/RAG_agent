import json
import os
from typing import Sequence

from click import prompt
from langchain_community.chat_models import ChatTongyi
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from requests import session


def get_history(session_id):
    return FileChatMessageHistory(session_id=session_id, storage_path="./chat_history")


class FileChatMessageHistory(BaseChatMessageHistory):

    def clear(self) -> None:
        with open(self.file_file, "w", encoding="utf-8") as f:
            json.dump([], f)

    def __init__(self, session_id, storage_path):
        self.session_id = session_id  # 会话id
        self.storage_path = storage_path  # 文件路径

        self.file_file = os.path.join(self.storage_path, self.session_id)
        # 确保路径存在
        os.makedirs(os.path.dirname(self.file_file), exist_ok=True)
        if not os.path.exists(self.file_file):
            with open(self.file_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # Sequence序列 类似 list、tuple
        print('adding messages')
        all_messages = list(self.messages)  # 获取现有消息
        all_messages.extend(messages)  # 添加新消息

        #将数据写入本地文件中
        # message_to_dict 将单个消息对象（BaseMessage）转换为字典格式
        new_messages = []
        for message in all_messages:
            new_messages.append(message_to_dict(message))
        # 简化写法
        # new_messages = [message_to_dict(message) for message in new_messages]

        with open(self.file_file, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False)

    @property
    def messages(self) -> Sequence[BaseMessage]:
        print('getting messages')
        try:
            with open(self.file_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                messages_data = json.loads(content)  #返回值： list[字典]
                #messages_from_dict 将dict -> BaseMessage
                return messages_from_dict(messages_data)
        except (FileNotFoundError, json.JSONDecodeError):
            return []


#
# 测试 class
os.environ["DASHSCOPE_API_KEY"] = "sk-fbfd1d070d274910b40189a2724f001d"

model = ChatTongyi(model='qwen3-max')

str_parser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ('system', '你需要根据会话历史回答问题'),
    MessagesPlaceholder('chat_history'),
    ('human', '{input}')
])

base_chain = prompt | model | str_parser

conversation_chain = RunnableWithMessageHistory(
    base_chain, #增强原有chat
    get_history, # 通过会话id获取InmemoryChatMessageHistory
    input_messages_key='input',
    history_messages_key='chat_history',
)

if __name__ == '__main__':
    session_config = {
        "configurable": {
            "session_id": "user_001"
        }
    }
    res = conversation_chain.invoke({"input": "小明有两个猫"}, session_config)
    print(res)
    res = conversation_chain.invoke({"input": "小明有一个狗"}, session_config)
    print(res)