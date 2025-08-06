"""
Hilbert V2 训练索引
一、接口初始化
二、创建index(默认创建单个索引) 
三、训练索引
"""
from elemem_sdk import hilbert_client
import sys
import numpy as np
from test_IVF_index_create import Create_Index_Process

def train_index_process(client,index_name, nb, dim, nlist, base):
    """训练索引(仅IVF需要)"""
    try:
         
        print(f"\n=== 开始训练:{index_name}索引, nlist={nlist}, nb={nb},dim={dim} ===")
        
        client.train(
            name=index_name,
            data=base,
            nlist=nlist
        )
        print(f"已完成{index_name}索引训练！")
        

    except Exception as e:
        print(f"❌ [FAILED] dim={dim}, error={str(e)}")
        return False   


if __name__ == '__main__':

    if (len(sys.argv) < 7):
        print("Please input : dim(1~8192) & nb & nlist & index_name & replica_num & card_num")
        print("请注意,暴力搜索算法没有训练过程!")
        sys.exit(-1)

    try :
        dim = int(sys.argv[1])             
        nb = int(sys.argv[2])
        nlist = int(sys.argv[3])
        index_name = sys.argv[4]

        replica_num = int(sys.argv[5])
        card_num = int(sys.argv[6])
        index_count = 1

        index_type = 1


        
        np.random.seed(42)
        base = np.random.randn(nb, dim).astype(np.float32) #生成一个随机正态分布的浮点数32位二维数组
        # base = np.random.randn(nb, dim).astype(np.float16) #生成一个随机正态分布的浮点数16位二维数组

        #接口初始化
        client = hilbert_client.HilbertClient("127.0.0.1:7000")

        #创建索引
        _ , index_name = Create_Index_Process(client,index_name,index_type, dim, replica_num,index_count,card_num)     

        #训练索引
        
        train_index_process(client,index_name, nb, dim, nlist, base)

    except Exception as e :
        raise Exception("抛出异常 : ",str(e)) 
    

    

