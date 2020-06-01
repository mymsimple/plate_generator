# encoding='utf-8'

import os


def char_sort():
    with open("data/char_count.txt", "r", encoding="utf-8") as f:
        char_list = []
        c_list = []
        for line in f.readlines():
            line = line.replace("[","")
            line = line.replace("]", "")
            line = line.replace("'", "")
            #print("line:", line)
            char, c = line.split()
            char_list.append(char)
            c_list.append(int(c))
        print("char_list:",char_list)
        print("c_list:",c_list)

        char_dict = dict(zip(char_list,c_list))
        print("char_dict:", char_dict)

        char_dict_sort = sorted(char_dict.items(), key=lambda x: x[1], reverse=True)
        print("char_dict_sort:",char_dict_sort)

    return char_dict_sort



if __name__ == "__main__":
    char_dict_sort = char_sort()

    with open("data/char_sort.txt", "w", encoding="utf-8") as f:
        for c in char_dict_sort:
            print("c:", c)
            list1 = list(c)
            str1 = list1[0] + ' ' + str(list1[1])
            f.write(str1 + "\n")


