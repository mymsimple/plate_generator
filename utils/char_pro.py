#encoding='utf-8'

import os


provinces = ["琼", "贵", "云", "藏", "青", "新", "晋", "甘", "赣", "津", "宁", "沪",
             "桂", "闽", "豫", "黑", "湘", "京", "陕", "浙", "吉", "粤", "渝", "川",
             "辽", "鄂", "蒙"]

def extract_txt():
    txt_path = "data/train.txt"
    with open(txt_path, "r", encoding='utf-8') as f:
        i = 0
        j = 0
        k = 0
        lines = []
        m = 0
        for line in f.readlines():
            if m % 1000 == 0:
                print("已完成：", m)

                line = line.replace("\n", "")
                path, label = line.split()
                chinese = label[0]

                if chinese == "皖":
                    if i <= 25000:
                        i +=1
                        lines.append(line)
                    else:
                        continue
                if chinese == "鲁":
                    if j <= 25000:
                        j +=1
                        lines.append(line)
                    else:
                        continue
                if chinese == "苏":
                    if k <= 25000:
                        k +=1
                        lines.append(line)
                    else:
                        continue
                else:
                    lines.append(line)
                    print("")

    with open("data/extract.txt","w",encoding='utf-8') as f1:
        for l in lines:
            f1.write(str(l) + "\n")
    print("处理完成")



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
            path = os.path.join("data/enhance_txt/" + file)
            with open(path, "r", encoding='utf-8') as f:
                line = f.readline()
                line = line.replace("\n","")
                line = "data/ocr/train/" + file[:-4] + ".jpg" + " " + line
                lines.append(line)

    with open("data/enhance.txt","w",encoding='utf-8') as f1:
        for l in lines:
            f1.write(str(l) + "\n")
    print("处理完成")



if __name__ == "__main__":
    #merge_txt()

    extract_txt()