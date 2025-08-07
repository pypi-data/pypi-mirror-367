import bigOAINet as bigo
from mxupy import IM

def install():
    """
        安装 bigo
    """
    im = IM()
    
    # 创建内部表
    if (im := bigo.create_inner_tables()).error:
        print(im.msg)
        return im
    
    # 初始化内部数据
    if (im := bigo.init_inner_data()).error:
        print(im.msg)
        return im
    
    return im

def is_install():
    """
        检查是否安装
    """
    if (im := bigo.RegistryItemControl.inst().get_as_dict("bigo")).error:
        print(im.msg)
        return False
    
    return im.data and im.data["installed"]

if __name__ == "__main__":
    if (im := install()).error:
        print(im.msg)
        exit(1)
        
    if not is_install():
        print("未安装 bigo")
        exit(1)
    else:
        print("bigo 已安装")
