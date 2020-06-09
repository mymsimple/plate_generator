# encoding="utf-8"
import os
import cv2
import numpy as np
import random
import math
from PIL import Image, ImageDraw

'''
    随机抽取一张汽车背景图片，随机选择一张生成的车牌，将生成的车牌贴在汽车背景图片上，增加干扰线、干扰点、随机旋转和切边等，增加生成车牌的真实性
'''

# 颜色的算法是，产生一个基准，然后RGB上下浮动FONT_COLOR_NOISE
MAX_FONT_COLOR = 100    # 最大的可能颜色
FONT_COLOR_NOISE = 10   # 最大的可能颜色
POSSIBILITY_RESIZE = 0.5    # 图像压缩的比例
POSSIBILITY_ROTATE = 0.7    # 图像旋转的比例
POSSIBILITY_INTEFER = 0.8   # 需要被干扰的图片比例，包括干扰线和点
INTERFER_LINE_NUM = 10      # 最多干扰线
INTERFER_LINE_WIGHT = 2
INTERFER_POINT_NUM = 10     # 最多干扰点
MAX_WIDTH_HEIGHT = 15    # 最大切边
MIN_WIDTH_HEIGHT = 0     # 最小切边
ROTATE_ANGLE = 5      # 最大旋转角度


# 随机接受概率
def _random_accept(accept_possibility):
    return np.random.choice([True,False], p=[accept_possibility,1 - accept_possibility])

def _get_random_point(x_scope,y_scope):
    x1 = random.randint(0,x_scope)
    y1 = random.randint(0,y_scope)
    return x1, y1

# 产生随机颜色
def _get_random_color():
    base_color = random.randint(0, MAX_FONT_COLOR)
    noise_r = random.randint(0, FONT_COLOR_NOISE)
    noise_g = random.randint(0, FONT_COLOR_NOISE)
    noise_b = random.randint(0, FONT_COLOR_NOISE)

    noise = np.array([noise_r,noise_g,noise_b])
    font_color = (np.array(base_color) + noise).tolist()

    return tuple(font_color)


# 画干扰线
def randome_intefer_line(img,possible,line_num,weight):
    if not _random_accept(possible): return

    w,h = img.size
    draw = ImageDraw.Draw(img)
    line_num = random.randint(0, line_num)

    for i in range(line_num):
        x1, y1 = _get_random_point(w,h)
        x2, y2 = _get_random_point(w,h)
        _weight = random.randint(0, weight)
        draw.line([x1,y1,x2,y2],_get_random_color(),_weight)

    del draw



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



def rotate_bound(plate, background_image, possible):
    r = random.sample(range(MIN_WIDTH_HEIGHT, MAX_WIDTH_HEIGHT), 2)

    if not _random_accept(possible):
        background_image.paste(plate, (r[0], r[1]))
    else:
        plate_con = plate.convert("RGBA")
        p = Image.new('RGBA', (500, 200))
        p.paste(plate_con, (10, 10))
        angle = random.randrange(-ROTATE_ANGLE, ROTATE_ANGLE)
        plate_r = p.rotate(angle)

        r, g, b, a = plate_r.split()
        background_image.paste(plate_r, (4, 0), mask=a)

    return background_image


def image_resize(image, possible):
    if not _random_accept(possible): return image

    w, h = image.size
    image = image.resize((int(w / 2), int(h / 2)), Image.ANTIALIAS)
    return image


def main(bg_path, plate_path, data_txt_path, generator_path, generator_txt):
    files = os.listdir(bg_path)
    i = 0
    for file in os.listdir(data_txt_path):
        txt_path = os.path.join(data_txt_path + file)
        with open(txt_path, "r", encoding='utf-8') as f:
            label = f.readline()
            image = Image.open(os.path.join(plate_path + file[:-4] + '.jpg'))
            # 在整张图上产生干扰点和线
            randome_intefer_line(image, POSSIBILITY_INTEFER, INTERFER_LINE_NUM, INTERFER_LINE_WIGHT)
            # 随机抽取汽车背景图片
            file = np.random.choice(files)
            background_image = Image.open(os.path.join(bg_path + file))
            # 旋转
            background_image = rotate_bound(image, background_image, POSSIBILITY_ROTATE)
            # 压缩车牌
            background_image = image_resize(background_image, POSSIBILITY_RESIZE)

            i += 1
            path = os.path.join(generator_path + str(i) + ".jpg")
            background_image.save(path)

            plate_txt = os.path.join(generator_txt + str(i) + ".txt")
            with open(plate_txt, "w", encoding='utf-8') as f1:
                f1.write(str(label))




if __name__ == "__main__":
    bg_path = "data/bg/"              # 汽车背景图片路径
    plate_path = "data/data/"         # 生成原始车牌路径
    data_txt_path = "data/data_txt/"  # 生成原始车牌标签路径
    generator_path = "data/plate/"    # 生成样本车牌路径
    generator_txt = "data/plate_txt/" # 生成样本车牌标签路径

    main(bg_path, plate_path, data_txt_path, generator_path, generator_txt)
    print("处理完成")



## 测试
# if __name__ == "__main__":
#     path = "multi_val/bg/"
#     files = os.listdir(path)
#     file = np.random.choice(files)
#     background_image = Image.open(os.path.join(path + file))
#     plate = Image.open("multi_val/data/云QF5H7P_blue_False.jpg")
#
#     plate_con = plate.convert("RGBA")
#     p = Image.new('RGBA', (500, 200))
#     p.paste(plate_con, (10, 10))
#     plate_r = p.rotate(-5)
#
#     r, g, b, a = plate_r.split()
#     background_image.paste(plate_r, (4, 0), mask=a)
#     background_image.save("multi_val/newImg.png", "PNG")