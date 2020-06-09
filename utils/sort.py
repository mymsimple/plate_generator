# encoding='utf-8'

import os

'''
    按字符数量做排序，如下：
    ['京 7577']           冀 20417      
    ['津 3843']   =====>  京 7577
    ['冀 20417']          津 3843
'''

def char_sort(old_txt):
    with open(old_txt, "r", encoding="utf-8") as f:
        char_list = []
        c_list = []
        for line in f.readlines():
            line = line.replace("[","")
            line = line.replace("]", "")
            line = line.replace("'", "")

            char, c = line.split()
            char_list.append(char)
            c_list.append(int(c))

        char_dict = dict(zip(char_list,c_list))
        char_dict_sort = sorted(char_dict.items(), key=lambda x: x[1], reverse=True)

    return char_dict_sort


def main(old_txt,sort_txt):
    char_dict_sort = char_sort(old_txt)
    with open(sort_txt, "w", encoding="utf-8") as f:
        for c in char_dict_sort:
            list1 = list(c)
            str1 = list1[0] + ' ' + str(list1[1])
            f.write(str1 + "\n")



if __name__ == "__main__":
    old_txt = "data/char_count.txt"
    sort_txt = "data/char_sort.txt"
    main(old_txt,sort_txt)