# encoding:utf-8

import requests
import base64
import cv2,os
import logging
import numpy as np
#CFG = config.CFG

'''
   调用local 系统OCR相关接口
'''

logger = logging.getLogger("OCR Utils")

def cv2_to_base64(image):
    """
    nparray格式的图片转为base64（cv2直接读出来的就是）
    :param img_data:
    :return:
    """
    base64_str = cv2.imencode('.jpg', image)[1].tostring()
    base64_str = base64.b64encode(base64_str)
    return str(base64_str,"utf-8")


# 处理将请求中的base64转成byte数组，注意，不是numpy数组
def base64_2_bytes(base64_data):
    logger.debug("Got image ,size:%d", len(base64_data))
    # 去掉可能传过来的“data:image/jpeg;base64,”HTML tag头部信息

    index = base64_data.find(",")
    if index != -1: base64_data = base64_data[index + 1:]
    # print(base64_data)
    # 降base64转化成byte数组
    buffer = base64.b64decode(base64_data)
    logger.debug("Convert image to bytes by base64, lenght:%d", len(buffer))

    return buffer


def base64_2_image(base64_data):
    data = base64_2_bytes(base64_data)
    return bytes2image(data)


# 从web的图片RGB的byte数组，转换成cv2的格式
def bytes2image(buffer):
    logger.debug("从web读取数据，长度:%r", len(buffer))

    if len(buffer) == 0:
        logger.error("图像解析失败，原因：长度为0")
        return None

    # 先给他转成ndarray(numpy的)
    data_array = np.frombuffer(buffer, dtype=np.uint8)

    # 从ndarray中读取图片，有raw数据变成一个图片GBR数据,出来的数据，其实就是有维度了，就是原图的尺寸，如160x70
    image = cv2.imdecode(data_array, cv2.IMREAD_COLOR)

    if image is None:
        logger.error("图像解析失败")  # 有可能从字节数组解析成图片失败
        return None

    logger.debug("从字节数组变成图像的shape:%r", image.shape)

    return image


def detect(img_base64):
    #url = CFG['local']['url'] + "/detect/detect.ajax"
    url = "http://ai.creditease.corp/detect/detect.ajax"
    post_data = {"img": img_base64,
                 "sid": "iamsid",
                 "do_verbose": False,
                 'detect_model': 'psenet',
                 'output_type':'rect',
                 'do_preprocess': False
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=post_data, headers=headers)
    print("response:",response)
    data = response.json()
    print('data:', data)
    return data



def order_points(image,pts):
    '''
    返回的pts:[{'x': 2999, 'y': 278}, {'x': 2981, 'y': 278}, {'x': 2981, 'y': 250}, {'x': 2999, 'y': 250}]
    需要先转化成
    array[[2999, 278], [2981,278], [2981, 250], [2999,250]]
    '''

    # 初始化坐标点
    rect = np.zeros((4, 2), dtype="float32")
    print("pts:",pts)

    lists = []
    for p in pts:
        list1 = [p['x'], p['y']]
        lists.append(list1)
    print("lists:",lists)

    pts = np.array(lists)
    # 获取左上角和右下角坐标点
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    #print("rect[0]:",rect[0])
    #print("rect[2]:", rect[2])
    # cv2.rectangle(image, (rect[0][0],rect[0][1]), (rect[2][0],rect[2][1]), (0, 0, 255), 3)
    # cv2.imwrite(os.path.join('data/debug.jpg'), image)

    # 分别计算左上角和右下角的离散差值
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(image, pts):
    """
        根据四点坐标切出图片,并透射变换为矩形输出
    :param image:
    :param pts: 4,2格式的
    :return:
    """
    # 获取坐标点，并将它们分离开来
    rect = order_points(image,pts)
    (tl, tr, br, bl) = rect

    # 计算新图片的宽度值，选取水平差值的最大值
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # 计算新图片的高度值，选取垂直差值的最大值
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # 构建新图片的4个坐标点
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # 获取仿射变换矩阵并应用它
    M = cv2.getPerspectiveTransform(rect, dst)
    # 进行仿射变换
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # 返回变换后的结果
    return warped


def crop_img_with_area(image, pts):
    warped = four_point_transform(image, pts)
    # 添加面积输出
    return warped, warped.shape[0] * warped.shape[1]


'''
data: { 'code': '0', 
        'detect_info': [[{'x': 2999, 'y': 278}, {'x': 2981, 'y': 278}, {'x': 2981, 'y': 250}, {'x': 2999, 'y': 250}], 
                        [{'x': 2365, 'y': 1029}, {'x': 2365, 'y': 980}, {'x': 2394, 'y': 980}, {'x': 2394, 'y': 1029}],
                         [{'x': 360, 'y': 1227}, {'x': 360, 'y': 1073}, {'x': 453, 'y': 1073}, {'x': 453, 'y': 1227}], 
                         [{'x': 734, 'y': 1628}, {'x': 288, 'y': 1468}, {'x': 360, 'y': 1275}, {'x': 806, 'y': 1436}], 
                         [{'x': 933, 'y': 1498}, {'x': 933, 'y': 1470}, {'x': 1079, 'y': 1470}, {'x': 1079, 'y': 1498}]], 
         'message': 'success', 
         'sid': 'iamsid'
     }
'''

def main(img,data,file):
    image = base64_2_image(img)
    bboxes = data['detect_info']

    max_area = 0
    max_plate_image = None
    max_bbox = None
    i = 0
    for bbox in bboxes:
        plate_image, area = crop_img_with_area(image, bbox)
        if area > max_area:
            max_area = area
            max_plate_image = plate_image
            max_bbox = bbox

        if max_plate_image is None:
            logger.error("在图片中无法找到车牌")


    img_path = os.path.join("data/psenet/" + file)
    cv2.imwrite(img_path, max_plate_image)

    return max_area, max_plate_image, max_bbox

        # i = 0
        # for image in plate_image:
        #     i += 1
        #     cv2.imwrite(os.path.join("data/psenet/" + str(i) + ".jpg"), image)



if __name__ == '__main__':
    files = os.listdir("data/problem_images/")
    for file in files:
        path = os.path.join("data/problem_images/" + file)
        print("path:",path)
        img = cv2.imread(path)
        if img is not None:
            img_base64 = cv2_to_base64(img)
            data = detect(img_base64)
            main(img_base64, data, file)


# 测试
# if __name__ == '__main__':
#     img = cv2.imread("data_old/bj/black.jpg")
#     img_base64 = cv2_to_base64(img)
#     data = detect(img_base64)
#     main(img_base64, data)
