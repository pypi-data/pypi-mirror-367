from peewee import AutoField, CharField, IntegerField, ForeignKeyField
from mxupy import TreeEntityX
import bigOAINet as bigo

class RegistryCategory(TreeEntityX):
    """注册表分类"""
    registryCategoryId = AutoField()
    
    name = CharField()
    namePath = CharField()
    
    parent = ForeignKeyField('self', column_name='parentId', field='registryCategoryId', backref='children', on_delete='CASCADE', default=None, null=True)

    class Meta:
        database = bigo.db
        name = '注册表分类'