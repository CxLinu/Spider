import re
import jieba
import numpy
import pandas as pd
import csv
from pyecharts import Bar, WordCloud

Java_position = []
C_position = [] # C#
Python_position = []
HTML5_position = []
Android_position = []
IOS_position = []
all_advantage = []


def read_csv():
    # 读取文件内容
    with open(r'../data/lagou.csv', 'r', newline='') as f:
        # 读文件
        reader = csv.reader(f)
        i = 0
        for row in reader:
            if i != 0:
                if "大专" == row[5]:
                    row[5] = "大专及以下"
                if "不限" == row[4]:
                    row[4] = "经验不限"
                if "应届毕业生" == row[4]:
                    row[4] = "应届生"
                if "1年以下" == row[4]:
                    row[4] = "1年以内"
                all_advantage.append(row[6])
                if row[8] == '0':
                    Java_position.append(row)
                elif row[8] == '1':
                    C_position.append(row)  # C#
                elif row[8] == '2':
                    Python_position.append(row)
                elif row[8] == '3':
                    HTML5_position.append(row)
                elif row[8] == '4':
                    Android_position.append(row)
                else:
                    IOS_position.append(row)
            i = i + 1
        print('lagou一共有：' + str(i - 1) + '个')

    with open(r'../data/boss.csv', 'r', newline='') as f:
        # 读文件
        reader = csv.reader(f)
        i = 0
        for row in reader:
            if i != 0:
                if "中专/中技" == row[5] or "大专" == row[5] or "高中" == row[5]:
                    row[5] = "大专及以下"
                all_advantage.append(row[6])
                if row[8] == '0':
                    Java_position.append(row)
                elif row[8] == '1':
                    C_position.append(row)  # C#
                elif row[8] == '2':
                    Python_position.append(row)
                elif row[8] == '3':
                    HTML5_position.append(row)
                elif row[8] == '4':
                    Android_position.append(row)
                else:
                    IOS_position.append(row)
            i = i + 1
        print('boss一共有：' + str(i - 1) + '个')


def get_city(position):
    city = []
    for row in position:
        city.append(row[3])
    return city


def get_salary(position):
    salary = []
    for row in position:
        salary.append(row[2].replace("k", "").replace("K", ""))
    return salary


def get_education(position):
    education = []
    for row in position:
        education.append(row[5])
    return education


def get_workyears(position):
    workyears = []
    for row in position:
        workyears.append(row[4])
    return workyears


def get_WorldCloud():
    content = ''
    for advantage in all_advantage:
        if advantage != '':
            content = content + ',' + advantage
    # 去除多余字符
    content = re.sub(r'[^\w\s]', ' ', content)
    segment = content.split(' ')
    # print(segment)
    # pandas、numpy 统计每个词出现次数
    words_df = pd.DataFrame({'segment': segment})
    words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数": numpy.size})
    words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

    test = words_stat.head(100).values
    # 分解数据
    codes = [test[i][0] for i in range(0, len(test))]
    counts = [test[i][1] for i in range(0, len(test))]
    # 生成词云图
    wordcloud = WordCloud(width=1300, height=620, page_title="福利关键词")
    wordcloud.add("福利关键词", codes, counts, word_size_range=[20, 100], shape='pentagon')
    wordcloud.render('../chart/world_cloud.html')


def Position_Analyze(position,name):
    city_lists = {}
    education_lists = {}
    workyears_lists = {}
    city = get_city(position)
    education = get_education(position)
    workyears = get_workyears(position)
    salary = get_salary(position)
    key = []
    values = []
    for ct in city:
        city_lists[ct] = city.count(ct)
    for k, v in city_lists.items():
        key.append(k)
        values.append(v)
    bar1 = Bar('%s职位需求' % name, '数量', page_title='城市分布')
    bar1.use_theme('infographic')
    bar1.add('%s' % name, key, values, is_more_utils=True, is_datazoom_show=True, mark_point=['min', 'max'],
             xaxis_interval=0, xaxis_rotate=40, yaxis_rotate=30)

    values = []
    for ed in education:
        education_lists[ed] = education.count(ed)
    edu = ['硕士', '本科', '大专及以下', '学历不限']
    mark = [0]*4
    for i in range(0,len(edu)):
        for k, v in education_lists.items():
            if k == edu[i] and mark[i] == 0:
                values.append(v)
                mark[i] = 1
        if mark[i] == 0:
            values.append(0)
    bar2 = Bar('%s学历要求' % name, '数量', page_title='学历要求')
    bar2.use_theme('infographic')
    bar2.add('%s' % name, edu, values, is_more_utils=True, mark_point=['min', 'max'], yaxis_rotate=30)

    values = []
    for wy in workyears:
        workyears_lists[wy] = workyears.count(wy)
    wys = ['应届生', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
    mark = [0]*6
    for i in range(0,len(wys)):
        for k, v in workyears_lists.items():
            if k == wys[i] and mark[i] == 0:
                values.append(v)
                mark[i] = 1
        if mark[i] == 0:
            values.append(0)
    bar3 = Bar('%s经验要求' % name, '数量', page_title='经验要求')
    bar3.use_theme('infographic')
    bar3.add('%s' % name, wys, values, is_more_utils=True, mark_point=['min', 'max'], yaxis_rotate=30)

    max = [0] * 6
    min = [0] * 6
    leng = [0] * 6
    for i in range(0, len(salary)):
        s = salary[i].split('-')
        if len(s) == 2:
            if workyears[i] == wys[0]:
                max[0] = max[0] + int(s[1])
                min[0] = min[0] + int(s[0])
                leng[0] = leng[0] + 1
            elif workyears[i] == wys[1]:
                max[1] = max[1] + int(s[1])
                min[1] = min[1] + int(s[0])
                leng[1] = leng[1] + 1
            elif workyears[i] == wys[2]:
                max[2] = max[2] + int(s[1])
                min[2] = min[2] + int(s[0])
                leng[2] = leng[2] + 1
            elif workyears[i] == wys[3]:
                max[3] = max[3] + int(s[1])
                min[3] = min[3] + int(s[0])
                leng[3] = leng[3] + 1
            elif workyears[i] == wys[4]:
                max[4] = max[4] + int(s[1])
                min[4] = min[4] + int(s[0])
                leng[4] = leng[4] + 1
            else:
                max[5] = max[5] + int(s[1])
                min[5] = min[5] + int(s[0])
                leng[5] = leng[5] + 1
    for i in range(0, 6):
        if leng[i] == 0:
            continue
        max[i] = format(max[i]/leng[i], '.1f')
        min[i] = format(min[i]/leng[i], '.1f')

    bar4 = Bar('%s薪资水平' % name, '单位（k/千元）', page_title='薪水水平')
    bar4.use_theme('infographic')
    bar4.add('%s_Max' % name, wys, max, is_more_utils=True, mark_point=['min', 'max'], yaxis_rotate=30)
    bar4.add('%s_Min' % name, wys, min, is_more_utils=True, mark_point=['min', 'max'], yaxis_rotate=30)
    # vintage, macarons, infographic, shine和roma

    if name == "C#":
        name = "CSHARP"
    bar1.render('../chart/%s_city.html' % name)
    bar2.render('../chart/%s_education.html' % name)
    bar3.render('../chart/%s_workyears.html' % name)
    bar4.render('../chart/%s_salary.html' % name)


if __name__ == '__main__':
    read_csv()
    get_WorldCloud()
    Position_Analyze(Java_position, "Java")
    Position_Analyze(C_position, "C#")
    Position_Analyze(Python_position, "Python")
    Position_Analyze(HTML5_position, "HTML5")
    Position_Analyze(Android_position, "Android")
    Position_Analyze(IOS_position, "IOS")

