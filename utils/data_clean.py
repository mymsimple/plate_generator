# encoding='utf-8'

import os

'''
     统计车牌样本中各个字符的次数
'''

def compare(txt, writePath):
    '''
    判断文本文件中图片路径是否有重复
    :return:
    '''

    outfile = open(writePath, 'a+', encoding='utf-8')
    f = open(txt, 'r', encoding='utf-8')
    lines_seen = set()

    i = 0
    for line in f.readlines():
        i += 1
        if len(line) > 1:
            if line not in lines_seen:
                outfile.write(line)
                lines_seen.add(line)
                if i % 10 == 0:
                    print("已经处理行数：", i)



def split_char(writePath,splitPath):
    '''
    文档行太多，直接统计时间复杂度太高，这里将一个文本文件进行拆分，分别存在不同的文件里
    :param writePath:
    :param splitPath:
    :return:
    '''
    f = open(writePath, 'r', encoding='utf-8')
    s = ""
    j = 0
    i = 0
    for line in f.readlines():
        j += 1
        if len(line) != 0:
            file, label = line.split()
            label = label.replace("\n", "")
            s = s + label
            if j % 10 == 0:
                print("已经处理行数：", j)
                i += 1
                path = os.path.join(splitPath + str(i) + ".txt")
                with open(path,"w", encoding='utf-8') as f1:
                    f1.write(s)
                    s = ""

        path = os.path.join(splitPath + str(i+1) + ".txt")
        with open(path, "w", encoding='utf-8') as f2:
            f2.write(s)


def count_char(s):
    # 统计个数
    resoult = {}
    for i in s:
        resoult[i] = s.count(i)

    # 排序
    r_sort = sorted(resoult.items(), key=lambda x: x[1], reverse=True)
    return r_sort


def main(splitPath,countPath):
    '''
    遍历拆分的文件，分别进行各个字符数量统计，保存在对应的文件里
    :param splitPath:
    :param countPath:
    :return:
    '''
    m = 0
    for file in os.listdir(splitPath):
        file_path = os.path.join(splitPath + file)
        f = open(file_path, "r", encoding="utf-8")
        line = f.readline()
        r_sort = count_char(line)

        m += 1
        count_path = os.path.join(countPath + str(m) + ".txt")
        with open(count_path, "w", encoding="utf-8") as f1:
            for l in r_sort:
                list1 = list(l)
                str1 = list1[0] + ' ' + str(list1[1])
                f1.write(str1 + "\n")


def merge_counts(counts_txt, countPath, char_txt):
    '''
    将每个文件里的字符统计个数进行合并统计，输出最终的各字符数量统计文件
    :return:
    '''

    all_counts = []

    for line in counts_txt:
        n = 0
        line = line.replace("\n", "")
        print("要统计的字:",line)

        for file in os.listdir(countPath):
            file_path = os.path.join(countPath,file)

            f1 = open(file_path, "r", encoding="utf-8")
            for l in f1.readlines():
                char, counts = l.split()
                counts = counts.replace("\n", "")
                if line == char:
                    n = n + int(counts)

        # 统计完每一个字符的个数和，写入文档
        char_count = line + " "+ str(n)
        all_counts.append([char_count])
    with open(char_txt, "w", encoding="utf-8") as f2:
        for c in all_counts:
            f2.write(str(c) + "\n")

    print("处理完成")


# def test1():
#     with open("data/test_1.txt", "r", encoding="utf-8") as f:
#         s = ""
#         for line in f.readlines():
#             path,char = line.split()
#             char = char.replace("\n","")
#             s = s + char
#
#         # 统计个数
#         resoult = {}
#         for i in s:
#             resoult[i] = s.count(i)
#         print("resoult:",resoult)
#
#         # 排序
#         r_sort = sorted(resoult.items(), key=lambda x: x[1], reverse=True)
#         print("r_sort:",r_sort)
#
#         with open("data/test1.txt", "w", encoding="utf-8") as f1:
#             for l in r_sort:
#                 list1 = list(l)
#                 str1 = list1[0] + ' ' + str(list1[1])
#                 f1.write(str1 + "\n")




if __name__ == "__main__":
    # 服务器上的路径
    txt = 'data/ocr/train.txt'
    writePath = 'data/ocr/train_1.txt'
    splitPath = "data/ocr/split/"
    countPath = "data/ocr/count/"
    char_txt = "data/ocr/char_count.txt"

    counts_txt = ["京", "津", "冀", "晋", "蒙", "辽", "吉", "黑", "沪","苏",
                  "浙", "皖", "闽", "赣", "鲁", "豫", "鄂", "湘", "粤", "桂",
                  "琼", "渝", "川", "贵", "云", "藏", "陕", "甘", "青", "宁",
                  "新", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M',
                  'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


    # 第一步：删除文档重复行
    compare(txt, writePath)

    # 第二步：统计各个字符个数
    split_char(writePath,splitPath)

    # 第三步：分组统计放在不同txt文档
    main(splitPath, countPath)

    # 第四步：各字符统计求和
    merge_counts(counts_txt, countPath, char_txt)

    #测试
    #test1()