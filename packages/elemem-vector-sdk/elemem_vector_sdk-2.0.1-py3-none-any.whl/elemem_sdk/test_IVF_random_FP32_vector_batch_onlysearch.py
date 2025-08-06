from elemem_sdk import hilbert_client
import sys
import numpy as np
import faiss

def batch_hilbert_search_vector(client,index_name, nprobe, top_k, query):
    max_query_size=1000
    if len(query)>max_query_size:
        all_ivf_distances = []
        all_ivf_labels = []
        for i in range(0,len(query),max_query_size):
            query_part = query[i:i + max_query_size]
            distances, labels = client.search(index_name, query_part, top_k, nprobe)
            all_ivf_distances.append(distances)
            all_ivf_labels.append(labels)
            print(f"处理批次 {i//max_query_size + 1}/{(len(query) + max_query_size - 1)//max_query_size}")
        hilbert_ivf_distances = np.concatenate(all_ivf_distances)
        hilbert_ivf_labels = np.concatenate(all_ivf_labels)
        
    elif len(query)<=max_query_size:
        hilbert_ivf_distances, hilbert_ivf_labels = client.search(index_name, query, top_k, nprobe)
    
    print(f"批量搜索hilbert_ivf的distance和id: {hilbert_ivf_distances}, {hilbert_ivf_labels}", flush=True)
    return hilbert_ivf_distances, hilbert_ivf_labels

def faiss_bf_batch_search(normal_vectors, queries, dim: int,top_k: int):
    """
    FAISS暴力搜索(BF)基准
    """
    print("Building BF ground truth...", flush=True)
    index_flat = faiss.IndexFlatL2(dim)
    index_flat.add(normal_vectors)

    all_faiss_bf_distances, all_faiss_bf_labels = index_flat.search(queries, top_k)
    
    # print(f"每次query,faiss_BF的distance和id:{all_faiss_bf_distances},{all_faiss_bf_labels}", flush=True)
    return all_faiss_bf_distances, all_faiss_bf_labels
    # return [arr[0][1:].tolist() for arr in all_faiss_bf_distances],[arr[0][1:].tolist() for arr in all_faiss_bf_labels]

def faiss_ivf_batch_search(normal_vectors, queries, dim, nlist,top_k,nprobe=16):
    """
    FAISS IVF索引搜索
    """
    print("\nBuilding IVF index...", flush=True)
    quantizer = faiss.IndexFlatL2(dim)
    faiss_index_ivf = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_L2)
    faiss_index_ivf.train(normal_vectors)
    faiss_index_ivf.add(normal_vectors)
    faiss_index_ivf.nprobe = nprobe  # 设置搜索的聚类中心数
    
    all_faiss_ivf_distances, all_faiss_ivf_labels = faiss_index_ivf.search(queries, top_k)
    
    # print(f"每次query,faiss_ivf的distance和id:{all_faiss_ivf_distances},{all_faiss_ivf_labels}", flush=True)
    return all_faiss_ivf_distances, all_faiss_ivf_labels
    # return [arr[0][1:].tolist() for arr in all_faiss_ivf_distances],[arr[0][1:].tolist() for arr in all_faiss_ivf_labels]

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Please input : 1、dim(1~8192)  2、nprobe  3、nq  4、top_k  5、index_name")
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
        queries = {nq: np.random.randn(nq, dim).astype(np.float32)}

        # 接口初始化
        client = hilbert_client.HilbertClient("127.0.0.1:7000")
                                                                                        
        all_hilbert_ivf_distances, all_hilbert_ivf_labels= batch_hilbert_search_vector(client, index_name, nprobe, top_k, queries[nq])

      
        print("\n===== Hilbert IVF single搜索结果 =====")
        for qid, (distances, ids) in enumerate(zip(all_hilbert_ivf_distances, all_hilbert_ivf_labels)):
            print(f"\nQuery {qid}:")
            print(f"  Top-K IDs:      {ids[0].tolist()}") 
            print(f"  Top-K Distances: {distances[0].tolist()}") 

    except Exception as e:
        raise Exception("ERROR: ", str(e))