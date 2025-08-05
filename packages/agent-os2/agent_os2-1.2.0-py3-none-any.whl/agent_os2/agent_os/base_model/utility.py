# 获取保守tokens统计
def get_fallback_tokens(*messages, model="gpt-4o", initial_tokens=0)->int:
    """
    根据messages获取保守的tokens统计，借助tiktoken进行基本统计
    针对字符串消息进行简化处理
    
    args:
        *messages: 字符串消息列表
        model: 用于编码的模型名称，默认为gpt-4o
        initial_tokens: 初始token开销，用于不同类型处理器的格式开销，默认为0
    returns:
        总token数的保守估计
    """
    import tiktoken
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # 如果模型不支持，回退到gpt-4o的编码器
        encoding = tiktoken.encoding_for_model("gpt-4o")
    
    num_tokens = initial_tokens  # 添加初始开销，替代硬编码的3
    for message in messages:
        if message:  # 只处理非空消息
            num_tokens += len(encoding.encode(str(message)))
    
    return num_tokens
    

# 获取模型成本
def get_model_cost(model_name:str,prompt_tokens:int,completion_tokens:int) -> float:
    """
    根据配置文件获取模型成本，文件中是每1000token的美元计价
    """
    import json
    import os
    with open(os.path.join(os.path.dirname(__file__),"models_price.json"),"r") as f:
        model_cost:dict[str,dict[str,float]] = json.load(f)
    return model_cost.get(model_name,{}).get("input_price",0) * prompt_tokens / 1000 + model_cost.get(model_name,{}).get("output_price",0) * completion_tokens / 1000 #文件中是每1000token的美元计价