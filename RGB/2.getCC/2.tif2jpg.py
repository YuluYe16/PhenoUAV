#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Description: trans tif format to jpg format and crop it
  Author: yulu_ye16@163.com
'''

import matplotlib.pyplot as plt
import os
import cv2
import cv2.cv2 as cv
import numpy as np

def show(img):
    plt.imshow(img)
    plt.show()

def rotate_bound(image, angle):
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    return cv2.warpAffine(image, M, (nW, nH))

wd = "CC/"
date = "20211211"

imagesDirectory = wd + date + "/plots_tif"  # tiff图片所在文件夹路径
distDirectory = wd + date + "/plots_jpg"  # 要存放jpg格式的文件夹路径
if not os.path.exists(distDirectory):
    os.makedirs(distDirectory)
tif_list = [x for x in os.listdir(imagesDirectory) if x.endswith(".tif")]
for imageName in tif_list:
    #imageName = "R1_C2.tif"
    imagePath = os.path.join(imagesDirectory, imageName)
    image = cv.imread(imagePath, -1)  # 打开tiff图像
    imag = rotate_bound(image, -12)
    # 裁剪坐标为[y0:y1, x0:x1] [473,264]
    y0 = int(16/451*imag.shape[0])
    y1 = int(429/451*imag.shape[0])

    x0 = int(86/251*imag.shape[1])
    x1 = int(165/251*imag.shape[1])
    img = imag[y0:y1, x0:x1]
    cv.imwrite(os.path.join(distDirectory, imageName[:-4] + ".jpg"), img)
    print(imagePath)



