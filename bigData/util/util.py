
import json
import os
class Util(object):

    def __init__(self):
        pass

    # 判断是否为空
    @staticmethod
    def isNull(str):
        if str == '':
            return True
        if str is None:
            return True
        return False

if __name__ == '__main__':
    objs = [{"value": "江苏集萃药康生物科技有限公司3.72%股权（对应43.152万元出资额）", 'key': 'targetCompanyIndustry'},
           {"value": "17GQ20200030", 'key': 'id'},

           {"value": "江苏集萃药康生物科技有限公司", 'key': 'name'},

           {"value": [
               {"name": "南京老岩企业管理中心（有限合伙）", 'rate': '65.96'},
               {"name": "江苏省产业技术研究院有限公司", 'rate': '8.62'},
           ], 'key': 'agency', }

           ]
    print(os.getcwd())
    print(os.path.exists('../util/dump.text'))
    print(type(""))
    with open('../data/models.txt', 'r', encoding='utf-8') as fr:
        try:
            print(json.load(fr))
        except Exception as e:
            print('......还未创建模型......')
            print(e)
        fr.close()


