import chromadb
from chromadb.config import Settings

def create_collection(path, collection_name, ids, embeddings, documents):
    """
    创建collection
    :param path: 数据库存储路径
    :param collection_name: 集合名称
    :param ids: 数据id列表
    :param embeddings: 数据embedding列表
    :param documents: 数据内容列表
    """
    client = chromadb.PersistentClient(
        path=path,
        settings=Settings(
            anonymized_telemetry=False,  # 禁用遥测
            allow_reset=True,
            is_persistent=True
        )
    )
    collection = client.create_collection(
        name=collection_name
    )
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
    )

def get_collection_data(path, collection_name):
    """
    获取collection数据
    :param path: 数据库存储路径
    :param collection_name: 集合名称
    :return: 
      ids, embeddings, documents
    """
    client = chromadb.PersistentClient(
        path=path,
        settings=Settings(
            anonymized_telemetry=False,  # 禁用遥测
            allow_reset=True,
            is_persistent=True
        )
    )
    collection = client.get_collection(name=collection_name)
    collection_data = collection.get(include=["embeddings", "documents"])
    embeddings = np.array(collection_data["embeddings"])
    documents = collection_data["documents"]
    ids = collection_data["ids"]
    return ids, embeddings, documents