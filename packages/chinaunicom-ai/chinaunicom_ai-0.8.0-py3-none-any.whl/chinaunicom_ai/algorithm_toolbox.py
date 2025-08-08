from sklearn.neighbors import NearestNeighbors
import numpy as np
from sklearn.cluster import KMeans

def knn_algorithm(embeddings, ids, events, k=10, threshold=0.1):
    """
    knn算法
    :param embeddings: 数据embedding列表
    :param ids: 数据id列表
    :param events: 数据内容列表
    :param k: 为每个事件找到最相似的k个邻居
    :param threshold: 相似度阈值
    :return: 
      返回结果列表，如 [{"ids": [id1, id2, ...], "embeddings": [embedding1, embedding2, ...], "events": [event1, event2, ...]}, ...]
    """
    # 使用K近邻找到每个事件的最相似邻居
    knn = NearestNeighbors(n_neighbors=k, metric='cosine')
    knn.fit(embeddings)

    # 为每个事件找到最相似的k个邻居
    distances, indices = knn.kneighbors(embeddings)

    result = []
    # 分析高相似度的事件组
    for i in range(len(embeddings)):
        # 找到相似度大于阈值的事件
        similar_indices = indices[i][distances[i] < threshold]  # 距离越小越相似
        kdata = {}
        kids = []
        kembeddings = []
        kevents = []
        if len(similar_indices) > 1:
            for index in similar_indices:
                kids.append(ids[index])
                kembeddings.append(embeddings[index])
                kevents.append(events[index])
            kdata["ids"] = kids
            kdata["embeddings"] = kembeddings
            kdata["events"] = kevents
            result.append(kdata)
    return result

def kmeans_algorithm(embeddings=None, ids=None, events=None, n=10):
    """
    kmeans算法
    :param embeddings: 数据embedding列表
    :param ids: 数据id列表
    :param events: 数据内容列表
    :param n: 聚类数量
    :return: 
      返回结果列表，如 [{"event_id":event_id, "event_info":event_info, "weight":weight}, ...]
    """
    # 使用K-means聚类找出代表性样本
    num_clusters = min(n, len(embeddings))
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=n)
    cluster_labels = kmeans.fit_predict(embeddings)

    # 找出每个聚类的中心点和最接近中心的样本
    typical_id_list = []
    typical_event_list = []
    report_subject_list = []
    weight_list = []
    cluster_centers = kmeans.cluster_centers_

    for cluster_id in range(num_clusters):
        # 获取当前聚类的所有样本
        cluster_samples_idx = np.where(cluster_labels == cluster_id)[0]

        # 计算该聚类中每个样本到聚类中心的距离
        cluster_embeddings = embeddings[cluster_samples_idx]
        distances = np.linalg.norm(cluster_embeddings - cluster_centers[cluster_id], axis=1)

        # 找出最接近中心的样本
        closest_idx = cluster_samples_idx[np.argmin(distances)]
        typical_id_list.append(ids[closest_idx])
        typical_event_list.append(events[closest_idx])

        # 添加该聚类的大小作为权重
        weight = len(cluster_embeddings)
        weight_list.append(weight)

    typical_list = [{"event_id":typical_id_list[i], "event_info":typical_event_list[i], "weight":weight_list[i]} for i in range(num_clusters)]
    typical_list.sort(key=lambda item:item["weight"], reverse=True)
    return typical_list