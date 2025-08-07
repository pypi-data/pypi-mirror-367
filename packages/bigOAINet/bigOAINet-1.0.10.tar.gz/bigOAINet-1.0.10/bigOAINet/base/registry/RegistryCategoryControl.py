import mxupy as mu
import bigOAINet as bigo

from mxupy import IM, TreeEntityXControl

class RegistryCategoryControl(TreeEntityXControl):
    """注册表分类控制类"""
    
    class Meta:
        model_class = bigo.RegistryCategory
        
    def __init__(self):
        
        paths = [
            mu.TreeDataPath(
                nameFieldName="name",
                namePathFieldName="namePath",
                isAllowRepeat=False,
                isAllowRepeatOfAll=True
            ),
        ]
        
        super().__init__(td=mu.TreeData(idFieldName='registryCategoryId', paths=paths))
    
    def add_path(self, name_path):
        """
        按路径添加分类（自动创建不存在的父级）
        
        Args:
            name_path (str): 分类路径，例如 'becool/app/demo'
            
        Returns:
            IM: 操作结果对象，包含成功状态和错误信息
        """
        sup = super()
        def _do():
            
            im = IM()
            if not name_path:
                return im.set_error('添加失败，namePath为空')
            
            # 检查是否已存在
            im = sup.exists({'namePath': name_path})
            if im.data:
                return im
            
            # 逐级创建分类
            parts = name_path.split('/')
            parent_id = None
            for i in range(len(parts)):
                current_path = '/'.join(parts[:i+1])
                
                # 检查当前路径是否存在
                im = sup.get_one(where={'namePath': current_path})
                if im.error:
                    return im
                
                if not im.data:
                    # 创建不存在的分类
                    new_category = bigo.RegistryCategory(
                        parentId = parent_id,
                        name = parts[i],
                    )
                    im = sup.add(new_category)
                    if im.error:
                        return im
                    parent_id = im.data.registryCategoryId
                else:
                    parent_id = im.data.registryCategoryId
            
            return im
        
        return self.run(_do)
    
    def delete_by_id(self, registryCategoryId, recursive=True):
        """
        删除分类（自动检查子分类和注册项）
        
        Args:
            registryCategoryId (int): 要删除的分类ID
            recursive (bool): 是否递归删除子分类和注册项
            
        Returns:
            IM: 操作结果对象，包含以下情况：
                - 存在子分类时返回错误，包含子分类的ID列表
                - 存在注册项时返回错误，包含注册项的ID列表
                - 成功删除时返回成功状态
        """
        sup = super()
        def _do():
            
            im = IM()
            # 检查子分类
            if sup.exists({'parentId': registryCategoryId}).data:
                return im.set_error('删除失败，该分类下有子类')
            
            # 检查注册项
            if bigo.RegistryItemControl.inst().exists({'registryCategoryId': registryCategoryId}).data:
                return im.set_error('删除失败，该分类下有注册项')
            
            # 执行删除
            return sup.delete_by_id(registryCategoryId, recursive)
        
        return self.run(_do)
