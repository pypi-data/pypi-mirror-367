from elemem_sdk import hilbert_client
from datetime import datetime
import sys
import numpy as np
import faiss
import json

def faiss_bf_single_search(normal_vectors, queries, dim: int, nq, top_k: int):
    """
    FAISS暴力搜索(BF)基准
    """
    print("Building BF ground truth...", flush=True)
    index_flat = faiss.IndexFlatL2(dim)
    index_flat.add(normal_vectors)
   
    all_faiss_bf_distances = []
    all_faiss_bf_labels = []

    for i in range(nq):
        # print(queries[i])
        # print(queries[i].reshape(1, -1).astype('float32'))
        faiss_BF_distances, faiss_BF_labels = index_flat.search(queries[i].reshape(1, -1).astype('float32'), top_k)
        # print(f"faiss_BF_id{i}:{faiss_BF_labels},faiss_BF_distances{i}:{faiss_BF_distances}")
        all_faiss_bf_distances.append(faiss_BF_distances)
        all_faiss_bf_labels.append(faiss_BF_labels)
    
    # print(f"每次query,faiss_BF的distance和id:{all_faiss_bf_distances},{all_faiss_bf_labels}", flush=True)
    return all_faiss_bf_distances, all_faiss_bf_labels
    # return [arr[0][1:].tolist() for arr in all_faiss_bf_distances],[arr[0][1:].tolist() for arr in all_faiss_bf_labels]


def faiss_ivf_single_search(normal_vectors, queries, dim, nlist, nq, top_k,nprobe=16):
    """
    FAISS IVF索引搜索
    """
    print("\nBuilding IVF index...", flush=True)
    quantizer = faiss.IndexFlatL2(dim)
    faiss_index_ivf = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_L2)
    faiss_index_ivf.train(normal_vectors)
    faiss_index_ivf.add(normal_vectors)
    faiss_index_ivf.nprobe = nprobe  # 设置搜索的聚类中心数
    
    all_faiss_ivf_labels = []
    all_distance_ivf = []
    
    for i in range(nq):
        faiss_IVF_distance, faiss_ivf_labels = faiss_index_ivf.search(queries[i].reshape(1, -1).astype('float32'), top_k)
        all_distance_ivf.append(faiss_IVF_distance)
        all_faiss_ivf_labels.append(faiss_ivf_labels)
    
    # print(f"每次query,faiss_ivf的distance和id:{all_distance_ivf},{all_faiss_ivf_labels}", flush=True)
    return all_distance_ivf, all_faiss_ivf_labels
    # return [arr[0][1:].tolist() for arr in all_distance_ivf],[arr[0][1:].tolist() for arr in all_faiss_ivf_labels]

def single_hilbert_search_vector(client,index_name,nprobe,top_k,queries,nq):
    """向量搜索"""

    all_hilbert_ivf_labels = []
    all_hilbert_ivf_distances = []
    for i in range(nq): 
        # print(len(queries[i].reshape(1, -1).astype('float32')))
        # print("********************************")
        # print(queries[i].reshape(1, -1).astype('float32'))                                              
        hilbert_ivf_distances, hilbert_ivf_labels = client.search(
            index_name,       # 位置参数 name
            queries[i].reshape(1, -1).astype('float32'),     # 位置参数 queries
            k=top_k,          # 关键字参数 k
            nprob=nprobe       # 关键字参数 nprob
        )
        # print(f"Hilbert_IVF_id{i}:{hilbert_ivf_labels},Hilbert_IVF_distance{i}:{hilbert_ivf_distances}")
        # print("#############################################################")
        # print(hilbert_ivf_labels)
        all_hilbert_ivf_distances.append(hilbert_ivf_distances)
        all_hilbert_ivf_labels.append(hilbert_ivf_labels)
        # print(f"每次query,hilbert_ivf的distance和id:{all_hilbert_ivf_distances},{all_hilbert_ivf_labels}", flush=True)
    # return  [arr[0][1:].tolist() for arr in all_hilbert_ivf_distances],[arr[0][1:].tolist() for arr in all_hilbert_ivf_labels]
    # print(all_hilbert_ivf_labels)
    return all_hilbert_ivf_distances,all_hilbert_ivf_labels

def calculate_recall(true_neighbors, predicted_neighbors, k):
    """修正后的召回率计算函数"""
    recall_sum = 0.0
    n_queries = len(true_neighbors)
    # print(type(true_neighbors),type(predicted_neighbors))
    
    for i in range(n_queries):
        # 提取当前查询的ID数组（处理嵌套的NumPy数组）
        true_topk = true_neighbors[i][:k]  
        pred_topk = predicted_neighbors[i][:k]
        
        # 计算交集
        intersection = len(np.intersect1d(true_topk, pred_topk))
        # print("999999999999999999999999999999999999999999999999")
        recall_sum += intersection
        # print(recall_sum)
    # print(intersection)
    return recall_sum / (n_queries * k)  # 平均召回率
# def calculate_recall(pred_ids, true_ids):
#     """
#     计算召回率：预测结果中与真实结果重叠的比例
#     pred_ids: 模型预测的ID数组（形状：[nq, topk]）
#     true_ids: 基准结果的ID数组（形状：[nq, topk]）
#     """
#     if pred_ids.shape != true_ids.shape:
#         raise ValueError(f"形状不匹配！pred_ids={pred_ids.shape}, true_ids={true_ids.shape}")
    
#     total = pred_ids.size  # 总数量 = 查询数 × topk
#     correct = 0
    
#     for i in range(pred_ids.shape[0]):
#         # 计算第i个查询的重叠数量
#         correct += np.isin(pred_ids[i], true_ids[i]).sum()
    
#     return correct / total if total != 0 else 0.0


def distance_labels_save(distance_labels_list,nb,nq,top_k):
    """保存距离和标签数据"""
    # 解包参数
    all_faiss_bf_distances, all_faiss_bf_labels, \
    all_distance_ivf, all_faiss_ivf_labels, \
    all_hilbert_ivf_distances, all_hilbert_ivf_labels = distance_labels_list
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"Random_IVF_search_results_base{nb}_query{nq}_top_k{top_k}_{timestamp}.json"
    
    def format_data(arr):
        """将numpy数组转换为字符串表示"""
        if isinstance(arr, np.ndarray):
            return arr.round(6).tolist()
        elif isinstance(arr, list):
            return [x.round(6).tolist() if isinstance(x, np.ndarray) else x for x in arr]
        return arr
    
    # 构建JSON数据结构
    results = {
        "faiss_BF": {
            "distance": format_data(all_faiss_bf_distances),
            "id": format_data(all_faiss_bf_labels)
        },
        "faiss_IVF": {
            "distance": format_data(all_distance_ivf),
            "id": format_data(all_faiss_ivf_labels)
        },
        "hilbert_IVF": {
            "distance": format_data(all_hilbert_ivf_distances),
            "id": format_data(all_hilbert_ivf_labels)
        }
    }
    
    # 保存为JSON文件
    with open(json_filename, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"搜索结果已保存为 {json_filename}")
    return json_filename


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("""Please input : 1、dim(1~8192)  2、nprobe  3、nq  4、top_k  5、index_name""")
        sys.exit(-1)

    try:
        dim = int(sys.argv[1])             
        nprobe = int(sys.argv[2])
        nq = int(sys.argv[3])
        top_k = int(sys.argv[4])
        index_name = sys.argv[5] 
        

        index_count = 1
        index_type = 1
            
        np.random.seed(1234)
        # queries = {nq: np.random.randn(nq, dim).astype(np.float32)}
        # queries = [np.random.randn(nq, dim).astype(np.float32)]
        queries = list(np.random.randn(nq, dim).astype(np.float32))
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(queries)

        # # 接口初始化
        client=hilbert_client.HilbertClient("127.0.0.1:7000")

        #向量搜索
        all_hilbert_ivf_distances, all_hilbert_ivf_labels= single_hilbert_search_vector(client,index_name,nprobe,top_k,queries,nq)
        
        print("\n===== Hilbert IVF single搜索结果 =====")
        for qid, (distances, ids) in enumerate(zip(all_hilbert_ivf_distances, all_hilbert_ivf_labels)):
            print(f"\nQuery {qid}:")
            print(f"  Top-K IDs:      {ids[0].tolist()}") 
            print(f"  Top-K Distances: {distances[0].tolist()}") 

        

    except Exception as e:
        raise Exception("抛出异常 : ", str(e)) 