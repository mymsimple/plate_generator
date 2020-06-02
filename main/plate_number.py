"""
generate plate numbers
"""

import numpy as np
import cv2, os
from glob import glob

# provinces = ["京", "津", "冀", "晋", "蒙", "辽", "吉", "黑", "沪",
#              "苏", "浙", "皖", "闽", "赣", "鲁", "豫", "鄂", "湘",
#              "粤", "桂", "琼", "渝", "川", "贵", "云", "藏", "陕",
#              "甘", "青", "宁", "新"]

#provinces = ["琼", "贵", "云", "藏", "青", "新", "晋", "甘", "赣", "津", "宁", "沪","桂","闽"] # 14个汉字需生成20000张
#provinces = ["豫", "黑", "湘", "京", "陕", "浙", "吉", "粤", "渝", "川"] # 10个汉字需生成750张，增强到15000张
#provinces = ["辽", "鄂", "蒙"] # 3个汉字需生成500张，增强到10000张

# "港", "澳", "使", "领", "学", "警", "挂"]
digits = ['{}'.format(x + 1) for x in range(9)] + ['0']
letters = [chr(x + ord('A')) for x in range(26) if not chr(x + ord('A')) in ['I', 'O']]
#print('letters', digits + letters)


def random_select(data):
    return data[np.random.randint(len(data))]

#随机生成一个省市，再随机生成6位数字+字母，构成七位
def generate_plate_number_blue(length=7):
    plate = random_select(provinces)
    for i in range(length - 1):
        plate += random_select(digits + letters)
    return plate


def generate_plate_number_blue_copy(length=7):
    provinces = ["琼", "贵", "云", "藏", "青", "新", "晋", "甘", "赣", "津", "宁", "沪","桂","闽"]
    #provinces = ["豫", "黑", "湘", "京", "陕", "浙", "吉", "粤", "渝", "川"]
    #provinces = ["辽", "鄂", "蒙"]

    provinces = [val for val in provinces for i in range(1000)]
    plates = []
    for plate in provinces:
        for i in range(length - 1):
            plate += random_select(digits + letters)
        plates.append(plate)

    return plates



def generate_plate_number_yellow_gua():
    plate = generate_plate_number_blue()
    return plate[:6] + '挂'


def generate_plate_number_yellow_xue():
    plate = generate_plate_number_blue()
    return plate[:6] + '学'


def generate_plate_number_white():
    plate = generate_plate_number_blue()

    if np.random.random(1) > 0.5:
        return plate[:6] + '警'
    else:
        first_letter = random_select(letters)
        return first_letter + plate[1:]


def generate_plate_number_black_gangao():
    plate = generate_plate_number_blue()
    return '粤' + plate[1:6] + random_select(["港", "澳"])


def generate_plate_number_black_ling():
    plate = generate_plate_number_blue()
    return plate[:6] + '领'


def generate_plate_number_black_shi():
    plate = generate_plate_number_blue()
    return '使' + plate[1:]


# def get_images_all(test_data_path, exts=['.jpg', '.png', '.jpeg', '.JPG']):
#     '''
#     find image files in test data path
#     exts: list of ext, ['.jpg', '.png', '.jpeg', '.JPG']
#     :return: list of files found
#     '''
#     if not isinstance(exts, list):
#         exts = [exts]
#     exts = [('.' + x).replace('..', '.') for x in exts]
#
#     files = []
#     for parent, dirnames, filenames in os.walk(test_data_path):
#         for filename in filenames:
#             if os.path.splitext(filename)[-1] in exts and not 'ccpd_np' in parent:
#                 files.append(os.path.join(parent, filename))
#     files.sort()
#     print('Find {} images from {}'.format(len(files), test_data_path))
#     return files
#
#
# def get_annoation_txt(filename, input_size):
#     txt_filename = os.path.splitext(filename)[0] + '.txt'
#
#     img = cv2.imread(filename)
#     h, w = img.shape[:2]
#     rate = float(input_size) / h
#     img = cv2.resize(img, None, fx=rate, fy=rate)
#
#     txt = open(txt_filename, 'r').readlines()[0].replace(',', ' ')
#     polys = np.array(list(map(float, txt.split()))).reshape(-1, 2) * rate
#
#     if len(polys) == 2:
#         x1, y1, x2, y2 = polys.reshape(-1)
#         polys = np.array([[x1, y1],
#                           [x2, y1],
#                           [x2, y2],
#                           [x1, y2]])
#
#     return img, polys.tolist()


def board_bbox(polys):
    x1, y1 = np.min(polys, axis=0)
    x2, y2 = np.max(polys, axis=0)

    return [x1, y1, x2, y2]

if __name__ == '__main__':
    pass