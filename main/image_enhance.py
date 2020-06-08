# encoding:utf-8

import cv2,os,numpy as np,random
from skimage import exposure
from skimage import util
import ast
import math
from multiprocessing import Process, Pool

import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# import log_utils
# logger = log_utils.init_logger()

MIN_ROTATE_ANGLE = 1  # 旋转的最小角度
MAX_ROTATE_ANGLE = 20 # 旋转的最大角度
MIN_EDGE_HEIGHT = 5 # 切边的最小高度
MAX_EDGE_HEIGHT = 15 # 切边的最大高度
SMALL_KERNEL_WIDTH = 100


def sharpen(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)  # 锐化
    dst = cv2.filter2D(image, -1, kernel=kernel)
    return dst

def save_image(original_name,type,dst_image,label):
    prefix,subfix = os.path.splitext(original_name)
    f_name = os.path.join(enhance_images_path,prefix+"_"+type+subfix)
    # print("保存图像：",f_name)
    cv2.imwrite(f_name,dst_image)
    #保存文本标签
    txt_name = os.path.join(enhance_txt_path,prefix+"_"+type+'.txt')
    with open(txt_name, "w",encoding='utf-8') as f:
        f.write(str(label))



def _kernel(image):
    kernel = random.choice([(2, 1), (1, 2)])
    #print("Kernel:",kernel)
    return kernel

def filer2d(image):
    k = _kernel(image)
    # print("2D:",k)
    kernel = np.ones(k, np.float32) / (k[0] * k[1])
    return cv2.filter2D(image, -1, kernel)

def filer_avg(img):
    k = _kernel(img)
    blur = cv2.blur(img, k)  # 模板大小为3*5, 模板的大小是可以设定的
    # box = cv2.boxFilter(img, -1, (3, 3))
    return blur

def filter_gaussian(img):
    # 原来内核大小只支持奇数
    k = random.choice([(3, 1), (1, 3), (3, 3)])
    blur = cv2.GaussianBlur(img, k, 0)  # （5,5）表示的是卷积模板的大小，0表示的是沿x与y方向上的标准差
    return blur

def filter_median(img):
    k = random.choice([1,2,3])
    #print("median:",k)
    blur = cv2.medianBlur(img,k)  # 中值滤波函数
    return blur

def filter_bi(img):
    blur = cv2.bilateralFilter(img, 3, 5, 5)
    return blur

# 曝光处理：参考：https://blog.csdn.net/limiyudianzi/article/details/86980680
def hist(image):
    dst_image = exposure.equalize_hist(image)
    # print(dst_image)
    return np.array(dst_image*255,dtype= np.uint8)

def adapthist(image):
    dst_image = exposure.equalize_adapthist(image)
    return np.array(dst_image*255,dtype= np.uint8)

def gamma(image):
    return exposure.adjust_gamma(image, gamma=0.5, gain=1)

# 噪音函数： https://blog.csdn.net/weixin_44457013/article/details/88544918
def noise_gaussian(image):
    noise_gs_img = util.random_noise(image,mode='gaussian')
    # 靠，util.random_noise()返回的是[0,1]之间，所以要乘以255
    return np.array(noise_gs_img*255, dtype = np.uint8)

def noise_salt(image):
    noise_salt_img = util.random_noise(image,mode='salt')
    return np.array(noise_salt_img * 255, dtype=np.uint8)

def noise_pepper(image):
    temp = util.random_noise(image,mode='pepper')
    return np.array(temp * 255, dtype = np.uint8)

def noise_sp(image):
    temp = util.random_noise(image,mode='s&p')
    return np.array(temp * 255, dtype=np.uint8)

def noise_speckle(image):
    temp = util.random_noise(image,mode='speckle')
    return np.array(temp * 255, dtype=np.uint8)

def adaptive_threshold(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 将图像转化为灰度
    blurred = cv2.GaussianBlur(image, (5, 5), 0)  # 高斯滤波
    # 自适应阈值化处理
    # cv2.ADAPTIVE_THRESH_MEAN_C：计算邻域均值作为阈值
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
    return thresh

#dimming
def darker(image,percetage=0.9):
    image_copy = image.copy()
    #get darker
    image_copy = image_copy * percetage
    image_copy = image_copy.astype(np.int32)
    return image_copy

def noise(img):
    for i in range(20): #添加点噪声
        temp_x = np.random.randint(0,img.shape[0])
        temp_y = np.random.randint(0,img.shape[1])
        img[temp_x][temp_y] = np.random.randint(255)
    return img

# 腐蚀和膨胀：https://blog.csdn.net/hjxu2016/article/details/77837765
def erode(img):
    k = _kernel(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,k)
    img = cv2.erode(img,kernel)
    return img

def dilate(img):
    k = _kernel(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,k)
    img = cv2.dilate(img,kernel)
    return img

# Gamma图像增强,https://blog.csdn.net/wujuxKkoolerter/article/details/96629463
def adjust_gamma(src,gamma=2.0):
    scale = float(np.iinfo(src.dtype).max - np.iinfo(src.dtype).min)
    dst = ((src.astype(np.float32) / scale) ** gamma) * scale
    dst = np.clip(dst,0,255).astype(np.uint8)
    return dst


def rotate(image,scale=1.0):
    angle = random.randrange(MIN_ROTATE_ANGLE,MAX_ROTATE_ANGLE)
    (h, w) = image.shape[:2]  # 2
    # if center is None: #3
    center = (w // 2, h // 2)  # 4
    M = cv2.getRotationMatrix2D(center, angle, scale)  # 5

    # 防止旋转图像丢失
    sin = math.fabs(math.sin(math.radians(angle)))
    cos = math.fabs(math.cos(math.radians(angle)))
    h_new = int(w * sin + h * cos)
    w_new = int(h * sin + w * cos)
    M[0, 2] += (w_new - w) / 2
    M[1, 2] += (h_new - h) / 2
    # 旋转后边角填充
    # rotated = cv2.warpAffine(image, M, (w_new, h_new), borderMode=cv2.BORDER_REPLICATE)
    # 白背景填充
    rotated = cv2.warpAffine(image, M, (w_new, h_new), borderValue=(254, 254, 254))
    return rotated


'''
[(404, 1574), (430, 1428), (768, 1610), (740, 1756), '晋A14Y18']
===>
404,1574,430,1428,768,1610,740,1756,晋A14Y18
'''
# 先做切边，上下左右切边，返回的坐标也要跟着修改，切下边和右边，坐标不变
def cut_edge(image,label,file_name):
    e = random.randint(MIN_EDGE_HEIGHT, MAX_EDGE_HEIGHT)  # 随机产生要切边的大小
    #print("切边大小:",e)
    #print("车牌号:",label)
    # 原图的尺寸
    h,w,_ = image.shape
    #print("原图尺寸：",image.shape)

    # 切上边
    img_up = image[e:h, 0:w]
    #print("---------",file_name)
    cv2.imwrite(os.path.join(enhance_images_path + file_name[:-4] + '_up' + '.jpg'), img_up)
    with open(enhance_txt_path + file_name[:-4] + '_up' + '.txt', "w", encoding='utf-8') as f:
        f.write(str(label))

    # 切下边，坐标不变
    img_down = image[0:h-e, 0:w]
    cv2.imwrite(os.path.join(enhance_images_path + file_name[:-4] + '_down' + '.jpg'), img_down)
    with open(enhance_txt_path + file_name[:-4] + '_down' + '.txt', "w", encoding='utf-8') as f:
        f.write(str(label))

    # 切右边，坐标不变
    img_right = image[0:h, 0:w-e]
    cv2.imwrite(os.path.join(enhance_images_path + file_name[:-4] + '_right' + '.jpg'), img_right)
    with open(enhance_txt_path + file_name[:-4] + '_right' + '.txt', "w", encoding='utf-8') as f:
        f.write(str(label))

    # 切左边
    img_left = image[0:h, e:w]
    cv2.imwrite(os.path.join(enhance_images_path + file_name[:-4] + '_left' + '.jpg'), img_left)
    with open(enhance_txt_path + file_name[:-4] + '_left' + '.txt', "w", encoding='utf-8') as f:
        f.write(str(label))


def original(image):
    return image

enhance_method = [
    {"name": "原图", 'fun': original},
    {"name": "2D", 'fun': filer2d},
    {"name": "均值", 'fun': filer_avg},
    {"name": "高斯", 'fun': filter_gaussian},
    {"name": "双边", 'fun': filter_bi},
    {"name": "gamma", 'fun': gamma},
    {"name": "锐化", 'fun': sharpen},
    {"name": "高斯噪音", 'fun': noise_gaussian},
    {"name": "盐噪音", 'fun': noise_salt},
    {"name": "胡椒噪音", 'fun': noise_pepper},
    {"name": "SP噪音", 'fun': noise_sp},
    {"name": "speckle噪音", 'fun': noise_speckle},
    {"name": "腐蚀", 'fun': erode},
    {"name": "膨胀", 'fun': dilate},
    {"name": "噪音", 'fun': noise},
    {"name": "变暗", 'fun': darker},
    {"name": "gamma图像增强", 'fun': adjust_gamma},
    #{"name": "旋转", 'fun': rotate}
   # {"name": "切边", 'fun': cut_edge} # 分别从上下左右切边
]



def enhance(img):
    method = random.choice(enhance_method)
    dst_image = method['fun'](img)
    print("增强：", method['name'])
    return dst_image

def enhance_all_with_save(img,f_name,label):
    for method in enhance_method:
        # logger.debug("图像增强-开始：%s ,%s",method['name'],f_name)
        dst_image = method['fun'](img)
        save_image(f_name, method['name'], dst_image,label)
        # logger.debug("图像增强-结束：%s,%s",method['name'],f_name)



def do_folder(p_no,folder,image_list):
    for file_name in image_list:
        logger.info("线程：%r,读取图片：%s",p_no,file_name)
        # print('线程：',p_no,'读取的图片名称:', file_name)
        f_name = os.path.join(folder,file_name)
        #print('f_name:',f_name)
        img = cv2.imread(f_name)
        logger.info("处理图片名称：%s", f_name)

        with open(good_txt_path + file_name[:-4] + '.txt', "r", encoding='utf-8') as f:
            label = f.readline()
            logger.info("处理图片标签：%s", label)
            cut_edge(img, label, file_name)

        save_image(file_name,"原图",img,label)
        enhance_all_with_save(img,file_name,label)
        logger.info("线程：%r,处理图片结束：%s",p_no,file_name)



good_images_path = "data/plate/"
good_txt_path = "data/plate_txt/"
enhance_txt_path = "data/enhance_txt/"
enhance_images_path = "data/enhance/"


if __name__ == "__main__":
    # 线程数
    worker = 2
    if not (os.path.exists(enhance_images_path)):
        os.makedirs(enhance_images_path)
    if not (os.path.exists(enhance_txt_path)):
        os.makedirs(enhance_txt_path)
    image_all = os.listdir(good_images_path)

    # 分批多线程处理
    file_list_arr = np.array_split(image_all, worker)
    logger.info("线程数：%r",worker)
    p_no = 0
    pool = Pool(processes=worker)

    for img_list in file_list_arr:
        pool.apply_async(do_folder, args=(p_no,good_images_path,img_list))
        p_no += 1
    pool.close()
    pool.join()
    logger.info("程序处理结束，全部增强完毕！")



# 测试
    # label = [(432, 1442), (770, 1514), (760, 1670), (424, 1594), '湘B3CY92']
    # label = ast.literal_eval(label)
    # do_file("../data/images/31.jpg")
    # do_file("../data/images/2456.jpg")
    # do_file("../data/images/465.jpg")