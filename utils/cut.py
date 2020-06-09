# encoding='utf-8'

import cv2
import os
import numpy as np
import random

'''
    挑选几张不同颜色的汽车背景，切成小图，将生成的车牌贴在小图上，使生成的车牌更真实
'''

def show(img, title='无标题'):
    """
    本地测试时展示图片
    :param img:
    :param name:
    :return:
    """
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    font = FontProperties(fname='/Users/yanmeima/workspace/ocr/crnn/data/data_generator/fonts/simhei.ttf')
    plt.title(title, fontsize='large', fontweight='bold', FontProperties=font)
    plt.imshow(img)
    plt.show()


def get_patches(img):
    dim_w = 460
    dim_h = 160
    h, w = img.shape[:2]

    # 如果图像宽高小于256，补齐到256
    if h < dim_h:
        # copyMakeBorder(img,top,bottom,left,right,borderType,colar
        # 把图像边界补上白色
        img = cv2.copyMakeBorder(img, 0, dim_h - h, 0, 0, cv2.BORDER_CONSTANT, value=(255,255,255))
    if w < dim_w:
        img = cv2.copyMakeBorder(img, 0, 0, 0, dim_w - w, cv2.BORDER_CONSTANT, value=(255,255,255))

    h, w = img.shape[:2]

    #看是256的几倍
    hNum, wNum = int(h / dim_h), int(w / dim_w)

    hPatchStart = 0  # if hNum < 4 else 1
    wPatchStart = 0  # if wNum < 4 else 1
    hPatchEnd = hNum  # if hNum < 4 else hNum - 1
    wPatchEnd = wNum  # if wNum < 4 else wNum - 1
    backupIdx = []
    # 按照256x256去裁图像
    candidate_patches = []
    for hIdx in range(hPatchStart, hPatchEnd):
        for wIdx in range(wPatchStart, wPatchEnd):
            hStart = hIdx * dim_h
            wStart = wIdx * dim_w
            backupIdx.append((hStart, wStart))
            grayCrop = img[hStart:(hStart + dim_h), wStart:(wStart + dim_w)]
            candidate_patches.append(grayCrop)

    #patch_idxes = np.arange(0, len(candidate_patches))
    #print("patch_idxes:",patch_idxes)

    return candidate_patches


def main(dir):
    patches = []
    for file in os.listdir(dir):
        path = dir + file
        img = cv2.imread(path)
        candidate_patches = get_patches(img)
        patches = patches + candidate_patches

    return patches



if __name__ == "__main__":
    bj_dir = "data/bj/"
    patches_path = "multi_val/patches/"

    patches = main(bj_dir)
    i = 0
    for p in patches:
        i += 1
        path = os.path.join(patches_path + str(i) + ".jpg")
        cv2.imwrite(path, p)



# # 测试
# if __name__ == "__main__":
#     img_path = "data/bj/blue.jpg"
#     path, name = os.path.split(img_path)
#     file, ext = os.path.splitext(name)
#     img = cv2.imread(img_path)
#     candidate_patches = get_patches(img)
#
#     i = 0
#     for p in candidate_patches:
#         i += 1
#         cv2.imwrite(os.path.join("data/patches/" + file + "_" + str(i) + ".jpg"), p)
