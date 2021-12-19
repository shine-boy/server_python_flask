

# "%Y-%m-%d %H:%M:%S"
def isNull(obj):
    if obj is None:
        return True
    if obj=="":
        return True
    return False

def getKeys_dic(obj,keys=[]):

    result={}
    if obj is None:
        return None
    for key in keys:
        result[key]=obj[key]
    if len(result.keys())==0:
        return None
    return result
