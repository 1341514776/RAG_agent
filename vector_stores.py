from langchain_chroma import Chroma
import config
import os
import chromadb
# 替换为你的OpenAI API Key
os.environ["DASHSCOPE_API_KEY"] = "sk-fbfd1d070d274910b40189a2724f001d"


class VectorStoreService(object):
    def __init__(self, embedding):
        self.vector_store = Chroma(
            collection_name=config.collection_name,  # 向量数据库集合名称
            persist_directory=config.persist_directory,  # 向量数据库持久化目录
            embedding_function=embedding
        )  # 向量数据库
        self.embedding = embedding

    def get_retriever(self):
        """获取向量数据库检索器"""
        return self.vector_store.as_retriever(search_kwargs={"k": config.top_k})


def print_collection_data(limit=5, include_embedding_dim=True):
    """打印向量数据库中的数据（ID、metadata、文本预览、向量维度）"""
    client = chromadb.PersistentClient(path=config.persist_directory)
    collection = client.get_collection(config.collection_name)

    total = collection.count()
    print(f"集合名: {config.collection_name}")
    print(f"向量总数: {total}")

    if total == 0:
        print("集合为空")
        return

    query_limit = min(limit, total)
    include_fields = ["documents", "metadatas"]
    if include_embedding_dim:
        include_fields.append("embeddings")

    data = collection.get(limit=query_limit, include=include_fields)
    ids = data.get("ids", [])
    docs = data.get("documents", [])
    metas = data.get("metadatas", [])
    embeddings = data.get("embeddings", []) if include_embedding_dim else []

    for i in range(query_limit):
        doc = docs[i] if i < len(docs) else ""
        meta = metas[i] if i < len(metas) else {}
        print(f"\n--- 第{i + 1}条 ---")
        print("id:", ids[i] if i < len(ids) else None)
        print("metadata:", meta)

        if include_embedding_dim:
            vector = embeddings[i] if i < len(embeddings) else None
            dim = len(vector) if vector is not None else 0
            print("embedding_dim:", dim)

        preview = (doc[:120] + "...") if isinstance(doc, str) and len(doc) > 120 else doc
        print("document_preview:", preview)

# def format_document(docs):
#     if not docs:
#         return "没有找到相关资料"
#     formatted_docs = []
#     for doc in docs:
#         formatted_doc = f"文档片段: {doc.page_content}\n文档元数据: {doc.metadata}\n\n"
#         formatted_docs.append(formatted_doc)
#     return formatted_docs

if __name__ == "__main__":
    print_collection_data(limit=10)
