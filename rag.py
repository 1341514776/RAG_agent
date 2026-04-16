from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config
import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from file_history_store import get_history


os.environ["DASHSCOPE_API_KEY"] = "sk-fbfd1d070d274910b40189a2724f001d"

class RagService(object):
    def __init__(self): 

        self.vector_service = VectorStoreService(embedding=DashScopeEmbeddings(model=config.embedding_name))
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主,简介和专业的回答用户问题.参考资料: {context}"),
                ('system', "我提供用户的对话记录，如下："),
                MessagesPlaceholder('history'),
                ("human", "{question}")
            ]
        )
        self.chat_model = ChatTongyi(model=config.chat_model_name, temperature=0.7) # 聊天模型
        self.chain = self.__get_chain() 


    def __get_chain(self):
        """获取RAG链"""
        retriever = self.vector_service.get_retriever() # 获取向量检索器

        def format_document(docs):
            if not docs:
                return "没有找到相关资料"
            formatted_docs = []
            for doc in docs:
                formatted_doc = f"文档片段: {doc.page_content}\n文档元数据: {doc.metadata}\n\n"
                formatted_docs.append(formatted_doc)
            return formatted_docs

        def format_for_retriever(value):
            print("输入问题：", value)
            return value['question'] # 从输入中提取问题文本，传递给检索器进行查询

        def format_for_prompt(value):
            print("检索结果：", value)
            new_value = {}
            new_value['question'] = value['question']['question']
            new_value['history'] = value['question']['history']
            new_value['context'] = value['context']
            return new_value # 从检索结果中提取文档内容，传递给提示模板进行回答生成

        chain = ({
            "question": RunnablePassthrough(), # 输入直接传递
            "context": RunnableLambda(format_for_retriever) | retriever | format_document, # 使用检索器获取上下文
        } | RunnableLambda(format_for_prompt) | self.prompt_template | self.chat_model | StrOutputParser()) # 将上下文输入到提示模板中，并使用聊天模型生成回答

        conversation_chain = RunnableWithMessageHistory(
            chain, #增强原有chat
            get_history, # 通过会话id获取InmemoryChatMessageHistory
            input_messages_key='question',
            history_messages_key='history',
        )
        return conversation_chain

# if __name__ == "__main__":
#     rag_service = RagService()
#     question = "体重120斤,我应该穿什么尺码?"
#     session_config = {
#         "configurable": {
#             "session_id": "user_001"
#         }
#     }
#     res = rag_service.chain.invoke({'question': question}, session_config)
#     print(res)