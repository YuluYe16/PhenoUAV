# -*- coding: utf-8 -*-
# encoding: utf-8

'''
  Description: calculate the RGB index
  Author: yulu_ye16@163.com
'''

import cv2
import numpy as np
import joblib
import matplotlib.pyplot as plt
import os
import pandas as pd
from tqdm import trange
import warnings

def RGBvis(img_path, img_name):
    img = cv2.imread(img_path)
    b, g, r = cv2.split(img)
    img_rgb = cv2.merge([r, g, b])
    img_reshape = img.reshape([img_rgb.shape[0]*img_rgb.shape[1], img_rgb.shape[2]])
    predict = reSoil_svc.predict(img_reshape).astype(np.uint8) # SVM预测像素点类型
    rmsoil = predict.reshape(img_rgb.shape[0], img_rgb.shape[1])

    B = b*rmsoil
    B = B.astype(float)
    B[B == 0] = np.nan
    G = g*rmsoil
    G = G.astype(float)
    G[G == 0] = np.nan
    R = r*rmsoil
    R = R.astype(float)
    R[R == 0] = np.nan

    EXR = 1.4*R-G
    EXG = 2*G-R-B
    EXGR = 3*G-2.4*R-B
    MGRVI = (G**2-R**2)/(G**2+R**2)
    NGRDI = (G-R)/(G+R)
    RGRI = R/G
    CIVE = 0.441*R-0.881*G+0.385*B+18.78
    VARI = (G-R)/(G+R-B)
    GLA = (2*G-R-B)/(2*G+R+B)
    RGBVI = (G**2-B*R)/(G**2+B*R)

    VIdf = pd.DataFrame({'plot_id': img_name.split('.')[0],
                         "B": np.nanmean(B),
                         "G": np.nanmean(G),
                         "R": np.nanmean(R),
                        "EXR": np.nanmean(EXR),
                        "EXG": np.nanmean(EXG),
                        "EXGR": np.nanmean(EXGR),
                        "MGRVI": np.nanmean(MGRVI),
                        "NGRDI": np.nanmean(NGRDI),
                        "RGRI": np.nanmean(RGRI),
                        "CIVE": np.nanmean(CIVE),
                        "VARI": np.nanmean(VARI),
                        "GLA": np.nanmean(GLA),
                        "RGBVI": np.nanmean(RGBVI)
                            }, index=[0]
                           )

    return VIdf

def main(tif_path,out_path):
    tif_list = os.listdir(tif_path)
    list_sorted = sorted(tif_list, key=lambda x: (
                             int(x.split('R')[1].split('_')[0]),
                             int(x.split('C')[1].split('.')[0]))
                         )
    out_df = pd.DataFrame()
    for i in list_sorted:
        vi_path = os.path.join(tif_path, i)
        new = RGBvis(vi_path, i)
        out_df = pd.concat([out_df, new], axis=0)
    out_df.to_excel(os.path.join(out_path, "T3_VI.xlsx"), index=False)

if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    reSoil_svc = joblib.load(r"F:\yeyulu\pythonProject\RGB\SvmRemoveSoil.m")
    for date in ("20220607", "20220610", "20220613", "20220620", "20220623", "20220627", "20220630",
                 "20220704", "20220707", "20220714", "20220824", "20220830"):
        wd = 'F:/yeyulu/XJ_results/' + date + '/T3_jpg'
        out = 'F:/yeyulu/XJ_results/' + date
        main(wd, out)
        print(date + " finished!")