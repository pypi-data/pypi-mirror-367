from peewee import ForeignKeyField
from playhouse.shortcuts import model_to_dict

from peewee import ForeignKeyField
from playhouse.shortcuts import model_to_dict

def model_to_dict_x(
    model,
    recurse=True,
    backrefs=False,
    only=None,
    exclude=None,
    max_depth=None,
    extra_attrs=None,
    **kwargs
):
    """
    增强版 model_to_dict，自动处理外键字段转换，同时支持所有原始参数
    
    参数:
        model: Peewee 模型实例
        recurse: 是否递归处理关联对象
        backrefs: 是否处理反向引用
        only: 只包含指定字段
        exclude: 排除指定字段
        max_depth: 递归最大深度
        extra_attrs: 包含额外属性
        **kwargs: 其他传递给原始 model_to_dict 的参数
    
    返回:
        转换后的字典
    """
    if isinstance(model, dict):
        return model
    
    if exclude is None:
        exclude = []
    
    # 获取所有字段
    fields = model._meta.fields
    
    if not recurse:
        # 找出所有外键
        fk_fields = []
        for field_name, field in fields.items():
            if isinstance(field, ForeignKeyField):
                exclude.append(field)
                fk_fields.append(field_name)
        
        # 确保外键字段不被原始 model_to_dict 处理
        exclude = list(set(exclude) | set(fk_fields))
        
        # 调用原始 model_to_dict
        data = model_to_dict(
            model,
            recurse=recurse,
            backrefs=backrefs,
            only=only,
            exclude=exclude,
            max_depth=max_depth,
            extra_attrs=extra_attrs,
            **kwargs
        )
        
        # 处理外键字段
        for field_name in fk_fields:
            field = fields[field_name]
            data[field.column_name] = getattr(model, field.column_name)
            
    else:
        data = model_to_dict(
            model,
            recurse=recurse,
            backrefs=backrefs,
            only=only,
            exclude=exclude,
            max_depth=max_depth,
            extra_attrs=extra_attrs,
            **kwargs
        )
    
    return data

def model_to_dict_x1(model):
    """
    将Peewee Model转换为字典，并自动处理外键字段
    
    Args:
        model: Peewee Model实例
    """
    exclude = []
    
    # 获取所有字段
    fields = model._meta.fields
    
    # 找出所有外键
    fk_fields = []
    for field_name, field in fields.items():
        if isinstance(field, ForeignKeyField):
            exclude.append(field)
            fk_fields.append(field_name)
    
    # 转换为基本字典
    data = model_to_dict(model, exclude=exclude, only=None)
    
    # 处理外键字段
    for field_name in fk_fields:
        field = fields[field_name]
        data[field.column_name] = getattr(model, field.column_name)
    
    return data