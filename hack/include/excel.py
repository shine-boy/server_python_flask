# coding=utf-8
import numpy
import xlrd
import xlwt
import os
import re
import copy
def bifDate():
    bumen = {
        "高速": "张林",
        "大数据": "刘国宏",
        "一部": "姜林青 ",
        "二部": "许彦良",
        "三部": "陈帅"
    }

    names = {
        '宋贤贤': 883256,
        '何飞虎': 883244,
        '孙赵龙': 883257,

        '陶洁': 883181,
        '吴留敏': 883212,

        '谭明成': 883249,
        '张熙': 883263,

        '关明哲': 883258,
        '魏健': 883261,
        '刘海飞': 883205,
        '刘鑫宇': 883204,

        '梁有琦': 883199,
        '张家博': 883272,
        '邹江': '无',
        '薛淇文': '无',
        '冷静': 883270,
        '李佳玉': 883266,
        '蔡啸新': 883252,
    }
    # 10-11月    2020-12月产业链工作量核算
    dir = 'C:\\Users\wu_lmin\Desktop\新建文件夹\\10-11月'
    dir_ = dir + "_"
    if not os.path.isdir(dir_):
        os.mkdir(dir_)
    for filename in os.listdir(dir):
        print(filename)
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            book = xlrd.open_workbook(dir + "/" + filename)
            sheetname = book.sheets()[0].name

            sheet = book.sheet_by_name(sheetname)
            rows = []
            for i in range(sheet.nrows):
                row = sheet.row_values(i)
                rows.append(row)
            rows[0][0] = filename.split("-")[1].split("月")[0] + "月开发"
            rows[1] = ['事业部', '对应事业部项目的项目名称', '对应事业部项目编号', '项目经理姓名', '人员姓名', '员工号', '开始时间', '结束时间', '实际工作日天数',
                       '当月工作日总数',
                       '人月单价', '结算金额', '职级认定', '备注']
            for r in rows[2:]:
                if r[0] == '':
                    rows.remove(r)
                    continue

                if r[1] == '':
                    r.insert(5, '')
                    r.insert(6, '')
                    if len(r) <= 14:
                        r.extend(numpy.array([''] * (14 - len(r))))
                    continue
                    #     学号
                r.insert(5, names.get(r[4]))
                print(r[6])
                temp = r[6].split('-')
                if len(temp) == 1:
                    temp = r[6].split('－')
                print(temp)
                startTime = temp[0].replace('.', '-')
                endTime = temp[1].replace('.', '-')
                r.insert(6, startTime)
                r[7] = endTime
                # 职级认定
                # 备注
                if len(r) <= 14:
                    r.extend(numpy.array([''] * (14 - len(r))))

                pass
            rows = rows[:-2]
            rows.append(['', '', '', '', '', '', '', '', '甲方：山东中创软件' + rows[2][0]])

            rows.append(['', '', '', '', '', '', '', '', '负责人'])
            rows.append(['', '', '', '', '', '', '', '', '乙方：昆山中创软件开发部'])
            rows.append(['', '', '', '', '', '', '', '', '地址：'])
            rows.append(['', '', '', '', '', '', '', '', '联系人：刘志勇'])
            rows.append(['', '', '', '', '', '', '', '', '联系电话：'])
            #
            for r in rows:
                print(r)
            result = xlwt.Workbook()
            sh = result.add_sheet(sheetname)
            for i in range(len(rows)):
                for j in range(len(rows[i])):
                    sh.write(i, j, label=rows[i][j])
            # if filename.endswith("xlsx"):
            #     filename=filename[:-1]
            result.save(dir_ + "/" + filename)

class array:
    @staticmethod
    def find(arr, target):
        try:
            i = arr.index(target)
            return arr[i]
        except Exception as e:
            return None

    @staticmethod
    def find_index(arr, target):
        if type(arr) is numpy.ndarray:
            arr = arr.tolist()
        try:
            return arr.index(target)
        except Exception as e:
            return -1

class Table:

    rows = numpy.empty(0)
    cols = numpy.empty(0)
    data = numpy.empty((1, 1))
    r_len = 0
    c_len = 0

    def push_row(self,row):
        self.r_len += 1
        self.rows = numpy.append(self.rows, row)
        if self.r_len != 1:
            self.data = numpy.append(self.data, numpy.empty((1, self.c_len)), axis=0)

    def push_col(self,col):
        self.c_len += 1
        self.cols = numpy.append(self.cols, col)
        if self.c_len != 1:
            self.data = numpy.append(self.data, numpy.empty((self.r_len, 1)), axis=1)

    def set(self, row, col, value):
        x = array.find_index(self.rows, row)
        y = array.find_index(self.cols, col)
        if x == -1:
            self.push_row(row)
            x = self.r_len - 1
        if y == -1:
            self.push_col(col)
            y = self.c_len - 1
        self.data[x][y] = value

    def get(self, row, col, default=None):
        x = array.find_index(self.rows, row)
        y = array.find_index(self.cols, col)
        if x == -1:
            return default
        if y == -1:
            return default
        return self.data[x][y]

    def write(self, sh, start_col):
        for j in range(self.c_len):
            sh.write(0, j+start_col, label=self.cols[j])
            for i in range(self.r_len):
                try:
                    sh.write(i+1, j+start_col, label=self.data[i][j])
                except Exception as e:
                    print(i)
                    print(j)
                    print(self.rows)
                    print(j+start_col)
                    print(self.data[i][j-start_col])
                    raise Exception('fd')


def fileToBBytes(file):
    filename = file.read()
    # with open(filename, 'rb', encoding='gbk') as inputFile:
    #
    #     return inputFile.read()
    # filename = filename.decode('utf-8', 'ignore')
    return filename



# 消化内科数据
def consume(defaultName=None,defaultHead=None,defaultFilter=None, file = None):
    # filename = 'C:\\Users\wu\Desktop\\servers_api.xlsx';
    filename = 'C:\\Users\wu\Documents\WeChat Files\wxid_iu41h1yc1i9422\FileStorage\File\\2021-11\消化内科数据.xlsx'

    if file:
        filename = fileToBBytes(file)
    print(filename)
    book = xlrd.open_workbook(filename)
    # 筛选
    def filter(head, data):
        for i in range(len(data[0])):
            if data[0][i] == head['source']:
                head['column'] = i
        for i in range(1, len(data)):
            if head['column'] == -1:
                continue
            try:
                if head.get('equal') != None:
                    if data[i][head['column']] == head.get('equal'):
                        head['data'].append(data[i]);
                        head['rows'].append(i + 1);
                    continue
                if head.get('keys') != None:

                    if re.match('.*(' + '|'.join(head['keys']) + ').*', data[i][head['column']]):
                        head['data'].append(data[i]);
                        head['rows'].append(i + 1);
                    continue
                if head.get('max') and head.get('min'):
                    if head.get('min') <= data[i][head['column']] <= head.get('max'):
                        head['data'].append(data[i]);
                        head['rows'].append(i + 1);
                    continue
                if head.get('min') != None:

                    if head.get('min') <= data[i][head['column']]:
                        head['data'].append(data[i]);
                        head['rows'].append(i + 1);
                    continue
                if head.get('max') != None:

                    if head.get('max') >= data[i][head['column']]:
                        head['data'].append(data[i]);
                        head['rows'].append(i + 1);
                    continue
                if head.get('month') != None:
                    if re.match('\d{8}(\.0)?', str(data[i][head['column']])):

                        if head.get('month') == int(str(data[i][head['column']])[4:6]):
                            head['data'].append(data[i]);
                            head['rows'].append(i + 1);
                        pass
                    continue
                if data[i][head['column']] == head.get('title'):
                    head['data'].append(data[i]);
                    head['rows'].append(i + 1);
            except Exception as e:
                pass
                print(e)
                # print(head)
                # print(data[i])
                # print(data[i][head['column']])

    # 递归 header规则
    def find(head, column):
        if head.get('filter') != None:
            for f in head['filter']:
                temp = [column]
                temp.extend(head['data'])

                if (len(temp) < 2):
                    break;
                filter(f, temp)
                find(f, column)

    def formatePrint(h):
        label = h.get('source')
        if h.get('title'):
            label = h.get('title')
        # print(label + ':' + str(len(h['rows'])))

    #  输出结果
    def headPrint(head):
        if head.get('filter'):
            for h in head.get('filter'):
                formatePrint(h)
                headPrint(h)

    sheetData=[]
    print(book.sheets())
    for sheet in book.sheets():
        sheetname = sheet.name
        print('----')
        print(sheetname)
        rows = []
        filter_ = copy.deepcopy(defaultFilter) if defaultFilter else [
            {
                            'title':'小于39',
                            'source': '年龄',
                            'column': -1,
                            'max': 39,
                            'filter': [
                                {
                                    'source': '性别',
                                    'title': '男',
                                    'equal': 1.0,
                                    'column': -1,
                                    'data': [],
                                    'rows': [],

                                },
                                {
                                    'source': '性别',
                                    'title': '女',
                                    'equal': 2.0,
                                    'column': -1,
                                    'data': [],
                                    'rows': [],

                                }
                            ],
                            'data': [],
                            'rows': [],
                        },
            {
                'title': '40-59',
                'source': '年龄',
                'column': -1,
                'max': 59,
                'min': 40,
                'filter': [
                    {
                        'source': '性别',
                        'title': '男',
                        'equal': 1.0,
                        'column': -1,
                        'data': [],
                        'rows': [],

                    },
                    {
                        'source': '性别',
                        'title': '女',
                        'equal': 2.0,
                        'column': -1,
                        'data': [],
                        'rows': [],

                    }
                ],
                'data': [],
                'rows': [],
            },
            {
                'title': '60-79',
                'source': '年龄',
                'column': -1,
                'max': 79,
                'min': 60,
                'filter': [
                    {
                        'source': '性别',
                        'title': '男',
                        'equal': 1.0,
                        'column': -1,
                        'data': [],
                        'rows': [],

                    },
                    {
                        'source': '性别',
                        'title': '女',
                        'equal': 2.0,
                        'column': -1,
                        'data': [],
                        'rows': [],

                    }
                ],
                'data': [],
                'rows': [],
            },
            {
                'title': '大于80',
                'source': '年龄',
                'column': -1,
                'min': 80,
                'filter': [
                    {
                        'source': '性别',
                        'title': '男',
                        'equal': 1.0,
                        'column': -1,
                        'data': [],
                        'rows': [],

                    },
                    {
                        'source': '性别',
                        'title': '女',
                        'equal': 2.0,
                        'column': -1,
                        'data': [],
                        'rows': [],

                    }
                ],
                'data': [],
                'rows': [],
            },
            {
                'source': '性别',
                'title': '男',
                'equal': 1.0,
                'column': -1,
                'data': [],
                'rows': [],

            },
            {
                'source': '性别',
                'title': '女',
                'equal': 2.0,
                'column': -1,
                'data': [],
                'rows': [],

            }
        ]
        header = copy.deepcopy(defaultHead) if defaultHead else {
            '疾病': [
                {

                    'title': '胃食管反流病',
                    'source': '主要诊断',
                    'keys': ["胃食管反流病", '反流性食管炎'],
                    'column': -1,
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '食管癌',
                    'source': '主要诊断',
                    'keys': ["食管癌", '食管恶性肿瘤'],
                    'column': -1,
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '贲门失弛缓',
                    'source': '主要诊断',
                    'keys': ["弛缓"],
                    'column': -1,
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '胃癌',
                    'source': '主要诊断',
                    'keys': ["胃癌", '胃恶性肿瘤'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '胃肠炎',
                    'source': '主要诊断',
                    'keys': ["胃炎", '肠炎'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '功能性胃肠病',
                    'source': '主要诊断',
                    'keys': ["功能性", '应激'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '消化道出血',
                    'source': '主要诊断',
                    'keys': ["出血"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '消化道溃疡',
                    'source': '主要诊断',
                    'keys': ["溃疡"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '消化道息肉',
                    'source': '主要诊断',
                    'keys': ["息肉"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '溃疡性结肠炎',
                    'source': '主要诊断',
                    'keys': ["溃疡性结肠炎", '炎症性肠病', '溃疡性小肠炎'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '克罗恩病',
                    'source': '主要诊断',
                    'keys': ["克罗恩"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '肠结核',
                    'source': '主要诊断',
                    'keys': ["肠结核", '结核性腹膜炎'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '白塞病',
                    'source': '主要诊断',
                    'keys': ["白塞"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '大肠癌',
                    'source': '主要诊断',
                    'keys': ["肠癌", '肠恶性肿瘤'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '胆道结石',
                    'source': '主要诊断',
                    'keys': ["结石"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '胆道感染',
                    'source': '主要诊断',
                    'keys': ["胆囊炎", '胆管炎'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '胰腺炎',
                    'source': '主要诊断',
                    'keys': ["胰腺炎", '胰腺假性囊肿'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '胰腺癌',
                    'source': '主要诊断',
                    'keys': ["胰腺癌", '胰腺恶性肿瘤'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '幽门螺旋杆菌感染',
                    'source': '主要诊断',
                    'keys': ["幽门螺旋"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '过敏性紫癜',
                    'source': '主要诊断',
                    'keys': ["紫癜"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '药物性肝病',
                    'source': '主要诊断',
                    'keys': ["药物性"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '自身免疫性肝病',
                    'source': '主要诊断',
                    'keys': ["自身免疫"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '乙肝肝硬化',
                    'source': '主要诊断',
                    'keys': ["乙肝"],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '脂肪性肝病',
                    'source': '主要诊断',
                    'keys': ["酒精", '脂肪肝'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '肝硬化',
                    'source': '主要诊断',
                    'keys': ["肝硬化", '感性脑病', '原发性肝病', '肝衰', '自发性腹膜炎'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '肝癌',
                    'source': '主要诊断',
                    'keys': ["肝癌", '肝恶性肿瘤'],
                    'column': -1,
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {

                    'title': '便秘',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ['便秘'],
                    'filter': filter_,
                    'data': [],
                    'rows': [],
                },
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
                # {
                #
                #     'title': '胃肠炎',
                #     'source': '主要诊断',
                #     'keys': ["胃炎", '肠炎'],
                #     'column': -1,
                #     'filter': [
                #         {
                #             'title':'小于40',
                #             'source': '年龄',
                #             'column': -1,
                #             'max': 40,
                #             'filter': [
                #                 {
                #                     'source': '性别',
                #                     'title': '男',
                #                     'equal': 1.0,
                #                     'column': -1,
                #                     'data': [],
                #                     'rows': [],
                #
                #                 },
                #                 {
                #                     'source': '性别',
                #                     'title': '女',
                #                     'equal': 2.0,
                #                     'column': -1,
                #                     'data': [],
                #                     'rows': [],
                #
                #                 }
                #             ],
                #             'data': [],
                #             'rows': [],
                #         }
                #     ],
                #     'data': [],
                #     'rows': [],
                # },
            ],
        }

        for i in range(sheet.nrows):
            row = sheet.row_values(i)
            rows.append(row)

        for key in header.keys():
            for head in header[key]:
                head['filter'] = copy.deepcopy(filter_);
                filter(head, rows)
                find(head, rows[0])

        for key in header.keys():
            pass
            for head in header[key]:
                formatePrint(head)
                headPrint(head)
        sheetData.append(header)
        pass

    result = xlwt.Workbook()

    sheetIndex = 1
    # 汇总表，取header第一层数据
    for key in header.keys():

        sh = result.add_sheet(key, cell_overwrite_ok=True )
        obj = Table()

        for sheet in book.sheets():
            header = sheetData[sheetIndex - 1]
            sh.write(0, sheetIndex, label=sheet.name)
            i = 1
            # 其中的所有分类皆放到一张表中
            child_sheet = None

            for head in header[key]:
                sh.write(i, 0, label=head.get('title'))
                sh.write(i, sheetIndex, label=len(head.get('rows')))
                if head.get('filter'):
                    if child_sheet is None:
                        child_sheet = result.add_sheet(sheet.name, cell_overwrite_ok=True )
                    fil_index = 1
                    for fil in head.get('filter'):
                        obj.set(head.get('title'), fil.get('title'),obj.get(head.get('title'), fil.get('title'), 0) + len(fil.get('rows')))
                        child_sheet.write(0, fil_index, label=fil.get('title'))
                        child_sheet.write(i, fil_index, label=len(fil.get('rows')))
                        fil_index += 1
                child_sheet.write(i, 0, label=head.get('title'))
                i+=1;
            sheetIndex+=1;
        obj.write(sh,start_col=sheetIndex)


    #
    # sh = result.add_sheet(sheetname)
    # for i in range(len(rows)):
    #     for j in range(len(rows[i])):
    #         sh.write(i, j, label=rows[i][j])
    name = defaultName if defaultName else 'testt123'
    if file:
        name = file.name
    saveFile = "./" + name + '.xls'
    if os.path.isfile(saveFile):
        os.remove(saveFile)
    result.save(saveFile)
    with open(saveFile, 'rb') as inputFile:
        print(os.path.abspath(saveFile))
        return inputFile.read()


    # # sheet.put_cell(1, 1, 1, "servers_api", 0)
    # print(sheet.row(0))
    # # for i in range(sheet.nrows):
    # #     row = sheet.row_values(i)
    # #     print(i, row)
    # #     count += 1
    # servers_api=openpyxl.open('C:\\Users\wu\Documents\Tencent Files\\3200456059\FileRecv\产业链\产业链\\6-9产业链核算/2020-6至9月产业链工作量核算（金二）.xlsx')
    # fd=servers_api.get_sheet_by_name('金融二部')
    # gf=openpyxl.Workbook().active

    # print(fd['A1'])

# 疾病
def jibing(file=None, filter=None, head=None):
    filter_ = [
        {
            'title': '7-17',
            'source': '年龄',
            'column': -1,
            'max': 17,
            'min': 7,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'title': '18-40',
            'source': '年龄',
            'column': -1,
            'max': 40,
            'min': 18,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'title': '41-65',
            'source': '年龄',
            'column': -1,
            'max': 65,
            'min': 41,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'title': '大于66',
            'source': '年龄',
            'column': -1,
            'min': 66,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'source': '性别',
            'title': '男',
            'equal': 1.0,
            'column': -1,
            'data': [],
            'rows': [],

        },
        {
            'source': '性别',
            'title': '女',
            'equal': 2.0,
            'column': -1,
            'data': [],
            'rows': [],

        }
    ]
    header = {
        '疾病': [
            {

                'title': '胃食管反流病',
                'source': '主要诊断',
                'keys': ["胃食管反流病", '反流性食管炎'],
                'column': -1,
                'filter': copy.deepcopy(filter_),
                'data': [],
                'rows': [],
            },
            {

                'title': '食管癌',
                'source': '主要诊断',
                'keys': ["食管癌", '食管恶性肿瘤'],
                'column': -1,
                'filter': copy.deepcopy(filter_),
                'data': [],
                'rows': [],
            },
            {

                'title': '贲门失弛缓',
                'source': '主要诊断',
                'keys': ["弛缓"],
                'column': -1,
                'filter': copy.deepcopy(filter_),
                'data': [],
                'rows': [],
            },
            {

                'title': '胃癌',
                'source': '主要诊断',
                'keys': ["胃癌", '胃恶性肿瘤'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '胃肠炎',
                'source': '主要诊断',
                'keys': ["胃炎", '肠炎'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '功能性胃肠病',
                'source': '主要诊断',
                'keys': ["功能性", '应激'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '消化道出血',
                'source': '主要诊断',
                'keys': ["出血"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '消化道溃疡',
                'source': '主要诊断',
                'keys': ["溃疡"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '消化道息肉',
                'source': '主要诊断',
                'keys': ["息肉"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '溃疡性结肠炎',
                'source': '主要诊断',
                'keys': ["溃疡性结肠炎", '炎症性肠病', '溃疡性小肠炎'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '克罗恩病',
                'source': '主要诊断',
                'keys': ["克罗恩"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '肠结核',
                'source': '主要诊断',
                'keys': ["肠结核", '结核性腹膜炎'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '白塞病',
                'source': '主要诊断',
                'keys': ["白塞"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '大肠癌',
                'source': '主要诊断',
                'keys': ["肠癌", '肠恶性肿瘤'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '胆道结石',
                'source': '主要诊断',
                'keys': ["结石"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '胆道感染',
                'source': '主要诊断',
                'keys': ["胆囊炎", '胆管炎'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '胰腺炎',
                'source': '主要诊断',
                'keys': ["胰腺炎", '胰腺假性囊肿'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '胰腺癌',
                'source': '主要诊断',
                'keys': ["胰腺癌", '胰腺恶性肿瘤'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '幽门螺旋杆菌感染',
                'source': '主要诊断',
                'keys': ["幽门螺旋"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '过敏性紫癜',
                'source': '主要诊断',
                'keys': ["紫癜"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '药物性肝病',
                'source': '主要诊断',
                'keys': ["药物性"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '自身免疫性肝病',
                'source': '主要诊断',
                'keys': ["自身免疫"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '乙肝肝硬化',
                'source': '主要诊断',
                'keys': ["乙肝"],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '脂肪性肝病',
                'source': '主要诊断',
                'keys': ["酒精", '脂肪肝'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '肝硬化',
                'source': '主要诊断',
                'keys': ["肝硬化", '感性脑病', '原发性肝病', '肝衰', '自发性腹膜炎'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '肝癌',
                'source': '主要诊断',
                'keys': ["肝癌", '肝恶性肿瘤'],
                'column': -1,
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {

                'title': '便秘',
                'source': '主要诊断',
                'column': -1,
                'keys': ['便秘'],
                'filter': filter_,
                'data': [],
                'rows': [],
            },
            {
                'source': '性别',
                'title': '男',
                'equal': 1.0,
                'column': -1,
                'data': [],
                'rows': [],

            },
            {
                'source': '性别',
                'title': '女',
                'equal': 2.0,
                'column': -1,
                'data': [],
                'rows': [],

            }
            # {
            #
            #     'title': '胃肠炎',
            #     'source': '主要诊断',
            #     'keys': ["胃炎", '肠炎'],
            #     'column': -1,
            #     'filter': [
            #         {
            #             'title':'小于40',
            #             'source': '年龄',
            #             'column': -1,
            #             'max': 40,
            #             'filter': [
            #                 {
            #                     'source': '性别',
            #                     'title': '男',
            #                     'equal': 1.0,
            #                     'column': -1,
            #                     'data': [],
            #                     'rows': [],
            #
            #                 },
            #                 {
            #                     'source': '性别',
            #                     'title': '女',
            #                     'equal': 2.0,
            #                     'column': -1,
            #                     'data': [],
            #                     'rows': [],
            #
            #                 }
            #             ],
            #             'data': [],
            #             'rows': [],
            #         }
            #     ],
            #     'data': [],
            #     'rows': [],
            # },
        ],

    }
    for i in range(12):
        filter_.append({
            'title': str(i + 1) + '月',
            'source': '入院时间',
            'month': i + 1,
            'column': -1,
            'data': [],
            'rows': [],
        })
        header['疾病'].append({

            'title': str(i + 1) + '月',
            'source': '入院时间',
            'month': i + 1,
            'column': -1,
            'filter': copy.deepcopy(filter_),
            'data': [],
            'rows': [],
        })
    return consume(defaultName='疾病分类', defaultHead=head or header,defaultFilter=filter or filter_, file= file);

# 外科诊室
def waike(file=None, filter=None, head=None):
    filter_ = [
        {
            'title': '小于39',
            'source': '年龄',
            'column': -1,
            'max': 39,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'title': '40-59',
            'source': '年龄',
            'column': -1,
            'max': 59,
            'min': 40,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'title': '60-79',
            'source': '年龄',
            'column': -1,
            'max': 79,
            'min': 60,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'title': '大于80',
            'source': '年龄',
            'column': -1,
            'min': 80,
            'filter': [
                {
                    'source': '性别',
                    'title': '男',
                    'equal': 1.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                },
                {
                    'source': '性别',
                    'title': '女',
                    'equal': 2.0,
                    'column': -1,
                    'data': [],
                    'rows': [],

                }
            ],
            'data': [],
            'rows': [],
        },
        {
            'source': '性别',
            'title': '男',
            'equal': 1.0,
            'column': -1,
            'data': [],
            'rows': [],

        },
        {
            'source': '性别',
            'title': '女',
            'equal': 2.0,
            'column': -1,
            'data': [],
            'rows': [],

        }
    ]
    header = {
        '外科诊所': [
                {
                    'title': '腹胀',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["腹胀"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '腹痛',
                    'source': '主要诊断',
                    'keys': ["腹痛"],
                    'column': -1,
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '腹泻',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["腹泻"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '呕吐',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["呕吐"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '黄疸',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["黄疸"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '呕血',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["呕血"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '黑便',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["黑便"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '便秘',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["便秘"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '消化道出血',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["出血"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '肝硬化',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["肝硬化"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '胆结石',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["结石"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '消化道溃疡',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["溃疡"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '肝损伤',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["肝损伤"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '胰腺炎',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["胰腺炎"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '消化道息肉',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["息肉"],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
                {
                    'title': '胃肠炎',
                    'source': '主要诊断',
                    'column': -1,
                    'keys': ["胃炎", '肠炎'],
                    'filter': copy.deepcopy(filter_),
                    'data': [],
                    'rows': [],
                },
            ]

    }
    return consume(defaultName='外科诊室', defaultHead=head or header,defaultFilter=filter or filter_, file=file);


if __name__ == '__main__':
   # consume()
   jibing()
   a = []
   a.append(3)
   print(a)


