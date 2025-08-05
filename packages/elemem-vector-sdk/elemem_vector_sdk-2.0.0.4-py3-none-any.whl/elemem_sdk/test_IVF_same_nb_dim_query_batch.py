"""
Hilbert V2 向量搜索
一、接口初始化
二、创建index(默认创建单个索引) 
三、训练索引
四、添加向量
    可分批添加向量
五、向量搜索
    搜索有两种模式：
    1、single
    2、batch
    输出recall:
    1、以faiss_BF为基准的recall
    2、以faiss_IVF为基准的recall
    保留所有distance、id数据
"""
from elemem_sdk import hilbert_client
import sys
import numpy as np
from test_IVF_index_create import Create_Index_Process
from test_IVF_index_train import train_index_process
from test_IVF_vector_add_random_FP32 import add_vectors
from test_IVF_random_FP32_vector_single_onlysearch import calculate_recall,distance_labels_save
from test_IVF_random_FP32_vector_batch_onlysearch import faiss_bf_batch_search ,faiss_ivf_batch_search,batch_hilbert_search_vector

def print_pairs(ids, distances, method_name):
            print(f"********************** {method_name} id/distance *******************************")
            for id_list, distance_list in zip(ids, distances):
                for id_val, distance_val in zip(id_list, distance_list):
                    print(f"ID: {id_val}, Distance: {distance_val}")

if __name__ == '__main__':

    if (len(sys.argv) < 11):
        print('Please input : nb & dim(1~8192) & nlist & nprobe & nq & top_k & replica_num(eg:0 or "0,8") & index_name & card_num & numbers!')
        sys.exit(-1)

    try :
        nb = int(sys.argv[1])
        dim = int(sys.argv[2])             
        nlist = int(sys.argv[3])
        nprobe = int(sys.argv[4])
        nq = int(sys.argv[5])
        top_k = int(sys.argv[6])
        # replica_num = int(sys.argv[7])
        replica_input = sys.argv[7]
        if ',' in replica_input:
            replica_num = list(map(int, replica_input.split(',')))
        else:
            replica_num = [int(replica_input)]  # 单个值转为列表形式

        index_name = sys.argv[8]
        card_num = int(sys.argv[9])
        numbers = int(sys.argv[10])

        
        index_type = 1
        index_count = 1
        
        np.random.seed(1234)
        vectors = np.random.randn(nb, dim).astype(np.float32)  #生成正态分布的32浮点数的二维数组
        # print(vectors.shape)
        queries = vectors[:nq]
        # print("queries.shape =", queries.shape)
        # # print(f"查询向量：{queries}")
        # faiss暴力搜索基准
        print("******************* faiss bf search *************************") 
        all_faiss_bf_distances, all_faiss_bf_labels = faiss_bf_batch_search (vectors, queries, dim, top_k)
        # print(nq)
        # print_bf_results(all_faiss_bf_labels, all_faiss_ivf_distances, nq, top_k) 
        # faiss ivf搜索结果
        print("******************* faiss ivf search *************************") 
        all_faiss_ivf_distances, all_faiss_ivf_labels = faiss_ivf_batch_search(vectors, queries, dim, nlist,top_k,nprobe)
        # print_bf_results(all_faiss_ivf_distances, all_faiss_ivf_labels, nq,top_k) 
        # print(nq)
        #接口初始化
        client = hilbert_client.HilbertClient("127.0.0.1:7000")

        #创建索引
        # all_index_names = []
        # for n in replica_num:
        #     if n >=1:
        #         index_name = f"{index_name}_replica_num_{n}"
        #         _ , index_names = Create_Index_Process(client,index_name,index_type, dim, n,index_count,card_num)
        #     elif n==0:
        #         _ , index_names = Create_Index_Process(client,index_name,index_type, dim, n,index_count,card_num)
        #     all_index_names.append(index_names)
        # print("All index names:",all_index_names) 
        # print(index_names)
        if len(replica_num) > 1:
            all_index_names = []
            for n in replica_num:
                index_name = f"{index_name}_replica_num_{n}"
                _ , index_names = Create_Index_Process(client,index_name,index_type, dim, n,index_count,card_num)
                all_index_names.append(index_names)
        elif len(replica_num)==1:
                _ , index_names = Create_Index_Process(client,index_name,index_type, dim,replica_num[0],numbers,card_num)
                # print("*******************************************************************")
                # print(index_names)
                all_index_names=index_names
                # print(all_index_names)
                
        print("All index names:",all_index_names) 
      
        #训练索引
        for i in range(len(all_index_names)):
            print(f"...................................................第{i}个索引开始训练...............................................")
            train_index_process(client,all_index_names[i], nb, dim, nlist, vectors)
        
            #向量添加
            print(f"...................................................给第{i}个索引添加向量...............................................")
            all_add_vectors = []
            add_vectors_ids = add_vectors(client,all_index_names[i], vectors)
            all_add_vectors.append(add_vectors_ids)
        # print(add_vectors_ids)

            #向量搜索                                                                        
            print(f"******************* 第{i}个索引的向量 hilbert ivf search *************************") 
            # hilbert_ivf_distances = []
            # hilbert_ivf_labels = []
            # print(index_names[i])
            # print(f"nq={nq}")
            all_hilbert_ivf_distances, all_hilbert_ivf_labels = batch_hilbert_search_vector(client,all_index_names[i],nprobe,top_k,queries)
            # print(f"nq={nq}")
            # print(f"第{i}次search的结果id输出如下:{all_hilbert_ivf_labels}")
            # hilbert_ivf_distances.append[all_hilbert_ivf_distances]
            # hilbert_ivf_labels.append[all_hilbert_ivf_labels]
            faiss_ivf_Recall_base_faiss_bf = calculate_recall(all_faiss_bf_labels, all_faiss_ivf_labels, top_k)
            hilbertv2_ivf_Recall_base_faiss_bf = calculate_recall(all_faiss_bf_labels, all_hilbert_ivf_labels, top_k)
            hilbertv2_ivf_Recall_base_faiss_ivf = calculate_recall(all_faiss_ivf_labels, all_hilbert_ivf_labels, top_k)
            # print(f"第{i}次search的recall计算结果输出如下:faiss_ivf_Recall_base_faiss_bf={faiss_ivf_Recall_base_faiss_bf},\nhilbertv2_ivf_Recall_base_faiss_bf={hilbertv2_ivf_Recall_base_faiss_bf},\nhilbertv2_ivf_Recall_base_faiss_ivf={hilbertv2_ivf_Recall_base_faiss_ivf}\n")
        # print("000000000000000000000000")

            print_pairs(all_faiss_bf_labels, all_faiss_ivf_distances, "FAISS暴力搜索(BF)")
            print_pairs(all_faiss_ivf_labels, all_faiss_ivf_distances, f"FAISS倒排索引(IVF)")
            print_pairs(all_hilbert_ivf_labels, all_hilbert_ivf_distances, f"Hilbert IVF 第{i}次")

            print("\n召回率统计:")
            print(f"FAISS IVF召回率 (基准BF): {faiss_ivf_Recall_base_faiss_bf}")
            print(f"第{i}次 Hilbert IVF召回率 (基准BF): {hilbertv2_ivf_Recall_base_faiss_bf}")
            print(f"第{i}次 Hilbert IVF召回率 (基准IVF): {hilbertv2_ivf_Recall_base_faiss_ivf}", flush=True)

        # distance_labels_list = [all_faiss_ivf_distances, all_faiss_bf_labels, 
        #        all_faiss_ivf_distances, all_faiss_ivf_labels,
        #        all_hilbert_ivf_distances, all_hilbert_ivf_labels]
        
        # distance_labels_save(distance_labels_list,nb,nq,top_k)

    except Exception as e :
        raise Exception("ERROR : ",str(e)) 
