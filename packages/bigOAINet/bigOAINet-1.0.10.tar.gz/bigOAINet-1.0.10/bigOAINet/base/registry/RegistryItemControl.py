import json
import dateutil.parser
import mxupy as mu
import bigOAINet as bigo

from mxupy import EntityXControl, IM

class RegistryItemControl(EntityXControl):
    """注册表项控制类"""
    
    class Meta:
        model_class = bigo.RegistryItem
    
    def get_by_category(self, registryCategoryId, page=1, size=20):
        """
        通过分类ID获取注册项列表
        
        Args:
            registryCategoryId (int): 分类ID
            page (int, optional): 页码，默认为1
            size (int, optional): 每页数量，默认为20
            
        Returns:
            IM: 包含查询结果的对象，data属性为RegistryItem列表
        """
        sup = super()
        def _do():
            # 获取所有子分类ID（包含自身）
            im = bigo.RegistryCategoryControl.inst().get_children_ids(registryCategoryId, include_self=True)
            if im.error:
                return im
            c_ids = im.data
            
            # 查询注册项
            return sup.get_list(
                where={'registryCategoryId': ('in', c_ids)},
                order_by=[('type', 'asc'), ('registryItemId', 'desc')],
                page=page,
                size=size
            )
        return self.run(_do)
    
    def get_by_path(self, name_path, key=None, limit=20, offset=0):
        """
        通过路径获取注册项
        
        Args:
            name_path (str): 分类路径（如'system/config'）
            key (str, optional): 注册项键名，不传则返回该路径下所有项
            page (int, optional): 页码，默认为1
            size (int, optional): 每页数量，默认为20
            
        Returns:
            IM: 包含查询结果的对象，data属性为RegistryItem列表或单个RegistryItem
        """
        sup = super()
        def _do():
            # 获取分类
            im = bigo.RegistryCategoryControl.inst().get_one(where={'namePath':name_path})

            if im.error:
                return im
            if not im.data:
                return im.set_error('分类不存在')
            category = im.data
            
            # 构建查询条件
            where = {'registryCategoryId': category.registryCategoryId}
            if key:
                where['key'] = key
            
            # 执行查询
            if key:
                return sup.get_one(where=where)
            else:
                return sup.get_list(
                    where=where,
                    limit=limit,
                    offset=offset
                )
        return self.run(_do)
    
    def add_or_update_item(self, name_path, key, value, item_type='string', mode='overwrite', desc=''):


        """
        添加或更新注册项
        
        Args:
            name_path (str): 分类路径（如'system/config'）
            key (str): 注册项键名
            value (str): 注册项值
            item_type (str, optional): 值类型，默认为'string'，可选：
                - 'string': 字符串
                - 'int': 整型
                - 'float': 浮点型
                - 'bool': 布尔值
                - 'date': 日期
            mode (str, optional): 操作模式，默认为'overwrite'，可选：
                - 'overwrite': 存在则覆盖
                - 'new': 总是创建新项
                - 'ignore': 存在则跳过
            desc (str, optional): 描述
            
                
        Returns:
            IM: 包含操作结果的对象
        """
        sup = super()
        def _do():
            # 确保分类路径存在
            im = bigo.RegistryCategoryControl.inst().add_path(name_path)
            if im.error:
                return im
            
            # 获取分类
            im = bigo.RegistryCategoryControl.inst().get_one(where={'namePath':name_path})
            if im.error:
                return im
            category = im.data
            
            # 检查key是否已存在
            im = sup.get_one(where=[
                {'registryCategoryId': category.registryCategoryId},
                {'key': key}
            ])
            if im.error:
                return im
            existing = im.data
            
            # 处理不同模式
            new_item = bigo.RegistryItem(
                registryCategoryId=category.registryCategoryId,
                key=key,
                value=value,
                type=item_type,
                desc=desc
            )
            
            if not existing:
                # 新增
                return sup.add(new_item)
            elif mode == 'new':
                # 强制新增
                return sup.add(new_item)
            elif mode == 'overwrite':
                # 更新
                new_item.registryItemId = existing.registryItemId
                return sup.update_by_id(existing.registryItemId, new_item)
            else:  # ignore
                return im.set_data(existing)
                
        return self.run(_do)
    
    def get_value(self, name_path, key, default=''):
        """
        获取注册项值
        
        Args:
            name_path (str): 分类路径
            key (str): 注册项键名
            default (str, optional): 默认值，当项不存在时返回
            
        Returns:
            str: 注册项的值或默认值
        """
        im = self.get_by_path(name_path, key)
        return im.data.value if im.data else default
    
    def get_as_dict(self, name_path):
        """
        获取路径下所有注册项并转为字典（自动按type字段转换值类型）
        
        Args:
            name_path (str): 分类路径
            
        Returns:
            dict: {key: converted_value} 格式的字典（值已按type转换）
                若出现错误返回空字典
        """
        im = self.get_by_path(name_path)
        if im.error or not im.data:
            return IM(True, '未找到注册项', {})

        type_converters = {
            'string': lambda x: str(x) if x is not None else '',
            'int': lambda x: int(x) if x not in (None, '') else 0,
            'float': lambda x: float(x) if x not in (None, '') else 0.0,
            'double': lambda x: float(x) if x not in (None, '') else 0.0,
            'bool': lambda x: str(x).lower() in ('true', '1', 'yes', 't'),
            'json': lambda x: json.loads(x) if x not in (None, '') else {},
            'list': mu.convert_to_list,
            'dict': lambda x: json.loads(x) if x not in (None, '') else {},
            'date': lambda x: dateutil.parser.parse(x).date(),
            'datetime': lambda x: dateutil.parser.parse(x)
        }

        result = {}
        for item in im.data:
            try:
                converter = type_converters.get(item.type.lower(), str)
                result[item.key] = converter(item.value)
            except (ValueError, json.JSONDecodeError, dateutil.parser.ParserError):
                continue

        return IM(True, '', result)


    def init_apiServer(self, configs = None):
        """
            初始化服务器配置
            
            Args:
                configs (list): 配置项列表
                
            Returns:
                IM: 初始化结果
        """
        # 配置服务器
        name_path = 'bigo/apiServer'
        cfs = [
            {
                "key": "host",
                "value": "0.0.0.0",
                "type": "string",
                "desc": "服务监听地址"
            },
            {
                "key": "port",
                "value": 8089,
                "type": "int",
                "desc": "服务监听端口"
            },
            {
                "key": "ssl_certfile",
                "value": "",
                "type": "string",
                "desc": "SSL证书文件路径"
            },
            {
                "key": "ssl_keyfile",
                "value": "",
                "type": "string",
                "desc": "SSL密钥文件路径"
            },
            {
                "key": "allow_credentials",
                "value": True,
                "type": "bool",
                "desc": "是否允许跨域凭据"
            },
            {
                "key": "allow_origins",
                "value": ["*"],
                "type": "list",
                "desc": "允许的跨域来源"
            },
            {
                "key": "allow_methods",
                "value": ["*"],
                "type": "list",
                "desc": "允许的HTTP方法"
            },
            {
                "key": "allow_headers",
                "value": ["*"],
                "type": "list",
                "desc": "允许的HTTP头部"
            },
            {
                "key": "debug",
                "value": True,
                "type": "bool",
                "desc": "调试模式开关"
            },
            {
                "key": "user_file_path",
                "value": "F://T",
                "type": "string",
                "desc": "用户文件存储路径"
            },
            {
                "key": "sys_file_path",
                "value": "F://T",
                "type": "string",
                "desc": "系统文件存储路径"
            },
            {
                "key": "web_file_path",
                "value": "",
                "type": "string",
                "desc": "Web文件存储路径"
            },
            {
                "key": "upload_file_size",
                "value": '{"image":3072, "audio":10240, "video":1024000}',
                "type": "dict",
                "desc": "上传文件大小限制(KB)"
            },
            {
                "key": "can_access_file_exts",
                "value": ['image','text'],
                "type": "list",
                "desc": "允许访问的文件扩展名"
            },
            {
                "key": "can_access_file_types",
                "value": ["*"],
                "type": "list",
                "desc": "允许访问的文件类型"
            },
            {
                "key": "access_file_max_age",
                "value": 31536000,
                "type": "int",
                "desc": "文件访问缓存最大年龄(秒)"
            }
        ]

        if not configs:
            configs = cfs
            
        # 批量添加/更新配置项
        for config in configs:
            config = mu.dict_to_obj(config)
            im = bigo.RegistryItemControl.inst().add_or_update_item(
                name_path=name_path,
                key=config.key,
                value=config.value,
                item_type=config.type,
                desc=config.desc,
                mode='overwrite'
            )
            
            if im.error:
                print(f"配置项 {config.key} 更新失败: {im.msg}")
            else:
                print(f"配置项 {config.key} 更新成功")
                
        return im

    def init_apiServer_accessToken(self, configs = None):
        """
            初始化服务器配置
            
            Args:
                configs (list): 配置项列表
                
            Returns:
                IM: 初始化结果
        """
        # 配置令牌
        name_path = 'bigo/apiServer/accessToken'
        cfs = [
            {
                "key": "expire_seconds",
                "value": 86400,
                "type": "int",
                "desc": "访问令牌过期时间（秒）"
            },
            {
                "key": "secret",
                "value": "fy,brysj198",
                "type": "string",
                "desc": "JWT签名密钥"
            },
            {
                "key": "algorithm",
                "value": "HS256",
                "type": "string",
                "desc": "JWT签名算法"
            },
            {
                "key": "issuer",
                "value": "bigoainet.com",
                "type": "string",
                "desc": "令牌签发者"
            },
            {
                "key": "audiences",
                "value": ["bigoainet.com", "bigoainet2.com"],
                "type": "list",
                "desc": "允许访问的域名列表"
            },
            {
                "key": "cache_max_size",
                "value": 1000,
                "type": "int",
                "desc": "令牌缓存最大数量"
            },
            {
                "key": "cache_ttl",
                "value": 86400,
                "type": "int",
                "desc": "令牌缓存有效期（秒）"
            }
        ]
        if not configs:
            configs = cfs
            
        # 批量添加/更新配置项
        for config in configs:
            config = mu.dict_to_obj(config)
            im = bigo.RegistryItemControl.inst().add_or_update_item(
                name_path=name_path,
                key=config.key,
                value=config.value,
                item_type=config.type,
                desc=config.desc,
                mode='overwrite'
            )
            
            if im.error:
                print(f"配置项 {config.key} 更新失败: {im.msg}")
            else:
                print(f"配置项 {config.key} 更新成功")
                
        return im
    
    def init_apiServer_member_user(self, configs = None):
        """
            初始化服务器配置
            
            Args:
                configs (list): 配置项列表
                
            Returns:
                IM: 初始化结果
        """
        # 配置令牌
        name_path = 'bigo/apiServer/member/user'
        cfs = [
            {
                "key": "login_fail_max_count",
                "value": 6,
                "type": "int",
                "desc": "登录失败最大次数"
            },
            {
                "key": "cache_max_size",
                "value": 1000,
                "type": "int",
                "desc": "登录缓存最大数量"
            },
            {
                "key": "cache_ttl",
                "value": 10,
                "type": "int",
                "desc": "登录缓存有效期（秒）"
            }
        ]
        
        if not configs:
            configs = cfs
            
        # 批量添加/更新配置项
        for config in configs:
            config = mu.dict_to_obj(config)
            im = bigo.RegistryItemControl.inst().add_or_update_item(
                name_path=name_path,
                key=config.key,
                value=config.value,
                item_type=config.type,
                desc=config.desc,
                mode='overwrite'
            )
            
            if im.error:
                print(f"配置项 {config.key} 更新失败: {im.msg}")
            else:
                print(f"配置项 {config.key} 更新成功")
                
        return im