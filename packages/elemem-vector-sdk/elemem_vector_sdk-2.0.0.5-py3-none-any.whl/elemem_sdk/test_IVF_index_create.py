"""
Hilbert V2 创建索引
一、接口初始化
二、创建index
    创建单个索引 or 创建多个索引
"""
from elemem_sdk import hilbert_client  
import sys

def Create_Index_Process(client,start_index_name, index_type, dim, replica_num, index_count,card_num):
    """创建索引,创建副本"""
    success_count = 0
    index_names = []
    
    if index_count == 1:
        client.create_index(start_index_name, dim, replica_num, index_type, card_num)
        print(f"✅ 成功创建索引: {start_index_name}")
        success_count = 1
        return success_count, start_index_name  # 直接返回字符串
        
    for i in range(index_count):
        new_index_name = f"{start_index_name}_{i}"
        try:
            # 显式转换所有数值参数
            client.create_index(new_index_name,dim,replica_num,index_type, card_num)
            success_count += 1
            index_names.append(new_index_name)
            print(f"新增索引: {new_index_name}!")
        except Exception as e:
            print(f"创建索引 {new_index_name} 失败: {str(e)}")
            # 打印更详细的错误信息
            if hasattr(e, 'details'):
                print(f"详细错误: {e.details()}")
    
    print(f"✅ {index_type} 索引创建结果: 成功 {success_count}/{index_count}")
    return success_count, index_names

if __name__ == '__main__':

    if (len(sys.argv) < 6):
        print("Please input : dim(1~8192)  & replica_num(0~8) & start_index_name & index_count & card_num !")
        sys.exit(-1)

    try :
        dim = int(sys.argv[1])             
        # index_type = int(sys.argv[2])
        replica_num = int(sys.argv[2])
        start_index_name = sys.argv[3]
        index_count = int(sys.argv[4])
        card_num = int(sys.argv[5])

        index_type = 1

        #接口初始化
        # HilbertClient(args.server, debug=True)
        client = hilbert_client.HilbertClient("127.0.0.1:7000")

        #创建索引
        index_created_count , index_names = Create_Index_Process(client,start_index_name,index_type, dim, replica_num,index_count,card_num)
        print(f"共创建了{index_created_count}个索引！")
        print(f"新增index列表如下:{index_names}")

    except Exception as e :
        raise Exception("ERROR : ",str(e)) 
    

