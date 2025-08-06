"""
Hilbert V2 向量添加
一、接口初始化
二、创建index(默认创建单个索引) 
三、训练索引
四、添加向量(向量为FP32浮点数)
"""
from elemem_sdk import hilbert_client
import sys
import numpy as np
from test_IVF_index_create import Create_Index_Process
from test_IVF_index_train import train_index_process

def add_vectors(client, index_name, vectors):
    """添加向量"""
    ids = []

    ids=client.add(
        name=index_name,
        data=vectors  
    )
    
    print("向量添加结束！")
    return ids
    


if __name__ == '__main__':

    if (len(sys.argv) < 7):
        print("""Please input : dim(1~8192) &  nb & index_name & replica_num & nlist & card_num """)
        sys.exit(-1)

    try :
        dim = int(sys.argv[1])             
        nb = int(sys.argv[2])
        index_name = sys.argv[3]

        replica_num = int(sys.argv[4])
        nlist = int(sys.argv[5])
        card_num = int(sys.argv[6])

        index_count = 1
        index_type = 1
        # add_times = 5
            
        
        # 生成随机向量
        vectors = np.random.randn(nb, dim).astype(np.float32)

       #接口初始化
        client = hilbert_client.HilbertClient("127.0.0.1:7000")

        #创建索引
        _ , index_names = Create_Index_Process(client,index_name,index_type, dim, replica_num,index_count,card_num)
      
        #训练索引
        train_index_process(client,index_names, nb, dim, nlist, vectors)
        
        #向量添加
        
        add_vectors_ids = add_vectors(client,index_names, vectors)

     

    except Exception as e :
        raise Exception("抛出异常 : ",str(e)) 
    




