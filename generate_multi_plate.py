import numpy as np
import cv2, os
from glob import glob


from plate_number import random_select, generate_plate_number_white, generate_plate_number_yellow_xue
from plate_number import generate_plate_number_black_gangao, generate_plate_number_black_shi, generate_plate_number_black_ling
from plate_number import generate_plate_number_blue, generate_plate_number_yellow_gua
from plate_number import letters, digits


def get_location_data(length=7, split_id=1, height=140):
    location_xy = np.zeros((length, 4), dtype=np.int32)

    if height == 140:
        location_xy[:, 1] = 25
        location_xy[:, 3] = 115
        step_split = 34 if length == 7 else 49
        step_font = 12 if length == 7 else 9

        width_font = 45
        for i in range(length):
            if i == 0:
                location_xy[i, 0] = 15
            elif i == split_id:
                location_xy[i, 0] = location_xy[i - 1, 2] + step_split
            else:
                location_xy[i, 0] = location_xy[i - 1, 2] + step_font
            if length == 8 and i > 0:
                width_font = 43
            location_xy[i, 2] = location_xy[i, 0] + width_font
    else:
        location_xy[0, :] = [110, 15, 190, 75]
        location_xy[1, :] = [250, 15, 330, 75]

        width_font = 65
        step_font = 15
        for i in range(2, length):
            location_xy[i, 1] = 90
            location_xy[i, 3] = 200
            if i == 2:
                location_xy[i, 0] = 27
            else:
                location_xy[i, 0] = location_xy[i - 1, 2] + step_font
            location_xy[i, 2] = location_xy[i, 0] + width_font

    return location_xy


def copy_to_image_multi(img, font_img, bbox, bg_color, is_red):
    x1, y1, x2, y2 = bbox
    font_img = cv2.resize(font_img, (x2 - x1, y2 - y1))
    img_crop = img[y1: y2, x1: x2, :]

    if is_red:
        img_crop[font_img < 200, :] = [0, 0, 255]
    elif 'blue' in bg_color or 'black' in bg_color:
        img_crop[font_img < 200, :] = [255, 255, 255]
    else:
        img_crop[font_img < 200, :] = [0, 0, 0]
    return img

class MultiPlateGenerator:
    def __init__(self, adr_plate_model, adr_font):
        self.adr_plate_model = adr_plate_model
        self.adr_font = adr_font

        self.font_imgs = {}
        font_filenames = glob(os.path.join(adr_font, '*jpg'))
        for font_filename in font_filenames:
            font_img = cv2.imread(font_filename, cv2.IMREAD_GRAYSCALE)

            if '140' in font_filename:
                font_img = cv2.resize(font_img, (45, 90))
            elif '220' in font_filename:
                font_img = cv2.resize(font_img, (65, 110))
            elif font_filename.split('_')[-1].split('.')[0] in letters + digits:
                font_img = cv2.resize(font_img, (43, 90))
            self.font_imgs[os.path.basename(font_filename).split('.')[0]] = font_img

        self.location_xys = dict()
        for i in [7, 8]:
            for j in [1, 2, 4]:
                for k in [140, 220]:
                    self.location_xys['{}_{}_{}'.format(i, j, k)] = \
                        get_location_data(length=i, split_id=j, height=k)

    def get_location_multi(self, plate_number, height=140):
        length = len(plate_number)
        if '警' in plate_number:
            split_id = 1
        elif '使' in plate_number:
            split_id = 4
        else:
            split_id = 2
        return self.location_xys['{}_{}_{}'.format(length, split_id, height)]

    def generate_plate_number(self):
        rate = np.random.random(1)
        if rate > 0.4:
            plate_number = generate_plate_number_blue(length=random_select([7, 8]))
        else:
            generate_plate_number_funcs = [generate_plate_number_white,
                                           generate_plate_number_yellow_xue,
                                           generate_plate_number_yellow_gua,
                                           generate_plate_number_black_gangao,
                                           generate_plate_number_black_shi,
                                           generate_plate_number_black_ling]
            plate_number = random_select(generate_plate_number_funcs)()

        bg_color = random_select(['blue'] + ['yellow'])

        if len(plate_number) == 8:
            bg_color = random_select(['green_car'] * 10 + ['green_truck'])
        elif len(set(plate_number) & set(['使', '领', '港', '澳'])) > 0:
            bg_color = 'black'
        elif '警' in plate_number or plate_number[0] in letters:
            bg_color = 'white'
        elif len(set(plate_number) & set(['学', '挂'])) > 0:
            bg_color = 'yellow'

        # is_double = random_select([False] + [True] * 3)
        is_double = True

        if '使' in plate_number:
            bg_color = 'black_shi'

        if '挂' in plate_number:
            is_double = True
        elif len(set(plate_number) & set(['使', '领', '港', '澳', '学', '警'])) > 0 \
                or len(plate_number) == 8 or bg_color == 'blue':
            is_double = False

        # special
        if plate_number[0] in letters and not is_double:
            bg_color = 'white_army'

        return plate_number, bg_color, is_double

    def generate_plate(self, enhance=False):
        plate_number, bg_color, is_double = self.generate_plate_number()
        height = 220 if is_double else 140

        # print(plate_number, height, bg_color, is_double)
        number_xy = self.get_location_multi(plate_number, height)
        img_plate_model = cv2.imread(os.path.join(self.adr_plate_model, '{}_{}.PNG'.format(bg_color, height)))
        img_plate_model = cv2.resize(img_plate_model, (440 if len(plate_number) == 7 else 480, height))

        for i in range(len(plate_number)):
            if len(plate_number) == 8:
                font_img = self.font_imgs['green_{}'.format(plate_number[i])]
            else:
                if '{}_{}'.format(height, plate_number[i]) in self.font_imgs:
                    font_img = self.font_imgs['{}_{}'.format(height, plate_number[i])]
                else:
                    if i < 2:
                        font_img = self.font_imgs['220_up_{}'.format(plate_number[i])]
                    else:
                        font_img = self.font_imgs['220_down_{}'.format(plate_number[i])]

            if (i == 0 and plate_number[0] in letters) or plate_number[i] in ['警', '使', '领']:
                is_red = True
            elif i == 1 and plate_number[0] in letters and np.random.random(1) > 0.5:
                # second letter of army plate
                is_red = True
            else:
                is_red = False

            if enhance:
                k = np.random.randint(1, 6)
                kernel = np.ones((k, k), np.uint8)
                if np.random.random(1) > 0.5:
                    font_img = np.copy(cv2.erode(font_img, kernel, iterations=1))
                else:
                    font_img = np.copy(cv2.dilate(font_img, kernel, iterations=1))

            img_plate_model = copy_to_image_multi(img_plate_model, font_img,
                                                  number_xy[i, :], bg_color, is_red)

        # is_double = 'double' if is_double else 'single'
        img_plate_model = cv2.blur(img_plate_model, (3, 3))

        return img_plate_model, number_xy, plate_number, bg_color, is_double


if __name__ == '__main__':
    generator = MultiPlateGenerator('plate_model', 'font_model')

    from tqdm import tqdm

    for i in tqdm(range(10000)):
        img, number_xy, gt_plate_number, bg_color, is_double = generator.generate_plate()

        if is_double and bg_color == 'yellow':
            cv2.imwrite('multi_val/{}_{}_{}.jpg'.format(gt_plate_number, bg_color, is_double), img)