import argparse
'''
    define the basic configuration parameters,
    also define one command-lines argument parsing method: init_args
'''

INPUT_IMAGE_HEIGHT = 64  # 图像归一化的高度
INPUT_IMAGE_WIDTH = 224  # 最大的图像宽度



def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="plate",type=str)
    parser.add_argument("--gen_path", default=None,type=str)
    parser.add_argument("--gen_label", default=None, type=str)
    parser.add_argument("--enhance_path", default=None, type=str)
    parser.add_argument("--enhance_label", default=None, type=str)
    args = parser.parse_args()

    return args


def init_gen_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image" ,default=1,type=str,help="")
    parser.add_argument("--model" ,default=1,type=str,help="")
    args = parser.parse_args()
    return args


