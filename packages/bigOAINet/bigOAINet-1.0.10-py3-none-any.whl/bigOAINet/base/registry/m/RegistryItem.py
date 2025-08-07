from peewee import AutoField, CharField, TextField, ForeignKeyField, IntegerField
from mxupy import EntityX
import bigOAINet as bigo

class RegistryItem(EntityX):
    """注册表项"""
    registryItemId = AutoField()
    
    # 类型
    type = CharField(default='string')
    
    # 键\值
    key = CharField()
    value = TextField(null=True)
    
    # 扩展数据\描述
    data = TextField(null=True)
    desc = TextField(null=True)
    
    # 分类
    registryCategory = ForeignKeyField(bigo.RegistryCategory, backref='registryItems', column_name='registryCategoryId', on_delete='CASCADE')
    
    @property
    def typeText(self):
        """类型文本"""
        type_map = {
            '': '未知',
            'string': '字符串',
            'int': '整型', 
            'float': '浮点型',
            'double': '双浮点型',
            'bool': '布尔',
            'json': 'JSON',
            'list': '列表',
            'dict': '字典',
            'date': '日期',
            'datetime': '时间'
        }
        return type_map.get(self.type, '未知')
    
    class Meta:
        database = bigo.db
        name = '注册表项'