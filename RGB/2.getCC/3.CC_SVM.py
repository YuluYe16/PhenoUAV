#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Description: calculate the canopy cover
  Author: yulu_ye16@163.com
'''

import cv2
import numpy as np
import joblib
import matplotlib.pyplot as plt
import os
import pandas as pd
from tqdm import trange

def find_files(input_directory, processed_files):
    files = os.listdir(input_directory)
    file_names = []
    for f in files:
        if f.endswith(
                ".jpg") and f not in processed_files:
            file_names.append(f)
    return file_names

def show(img):
    plt.imshow(img)
    plt.show()

def CC(img):
    img = cv2.imread(img)
    b, g, r = cv2.split(img)
    img_rgb = cv2.merge([r, g, b])
    img_reshape = img.reshape([img_rgb.shape[0]*img_rgb.shape[1], img_rgb.shape[2]])
    predict = reSoil_svc.predict(img_reshape).astype(np.uint8) # SVM预测像素点类型
    rmsoil = predict.reshape(img_rgb.shape[0], img_rgb.shape[1])*255
    cc = round(sum(sum(rmsoil/255))/(rmsoil.size), 2)
    return cc

def batch_CC(img_path):
    os.chdir(img_path)
    tif_list = sorted(os.listdir(img_path))
    list_sorted = sorted(tif_list,
                         key=lambda x: (
                         int(x.split('R')[1].split('_')[0]),
                         int(x.split('C')[1].split('.')[0]))
                         )
    out_df = pd.DataFrame()
    for i in trange(len(list_sorted), position=0):
        cc = CC(list_sorted[i])
        new = pd.DataFrame({'plot_id': list_sorted[i].split('.', 1)[0], 'CC'+ date: cc}, index=[0])

        out_df = pd.concat([out_df, new], axis=0)
    print("Canopy Cover extraction Finished!")
    return out_df

if __name__ == '__main__':
    wd = "CC/"
    date = "20211211"

    img_path = wd + date + '/plots_jpg'
    reSoil_svc = joblib.load(r"RGB\SvmRemoveSoil.m")
    cc = batch_CC(img_path)
    cc.to_excel(wd + date + '/CC.xlsx', index=False)
