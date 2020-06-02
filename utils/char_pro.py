#encoding='utf-8'

import os


def test():
    txt_path = "data/test/test_1.txt"
    with open(txt_path, "r", encoding='utf-8') as f:
        i = 0
        for line in f.readlines():
            path, label = line.split()
            #label = label.replace("\n", "")
            chinese = label[0]
            print("chinese:", chinese)

            if chinese == "皖":
                continue
            else:
                print("")


def merge_txt():
    files = os.listdir("data/enhance_txt/")
    lines = []
    i = 0
    for file in files:
        i +=1
        if i % 1000 == 0:
            print("已完成：",i)
        if file == ".DS_Store":continue
        else:
            #print("file:",file)
            path = os.path.join("data/enhance_txt/" + file)
            with open(path, "r", encoding='utf-8') as f:
                line = f.readline()
                line = line.replace("\n","")
                line = "data/ocr/train/" + file[:-4] + ".jpg" + " " + line
                #print("line:",line)
                lines.append(line)

    with open("data/enhance.txt","w",encoding='utf-8') as f1:
        for l in lines:
            f1.write(str(l) + "\n")
    print("处理完成")

if __name__ == "__main__":
    merge_txt()