import json

def round_raw_data(data, decimals=2):
    """格式化raw数据中的数值保留指定小数位"""
    def round_value(obj):
        if isinstance(obj, float):
            return round(obj, decimals)
        elif isinstance(obj, dict):
            return {k: round_value(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [round_value(item) for item in obj]
        return obj
    
    return round_value(data)