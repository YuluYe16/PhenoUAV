# -*- coding: utf-8 -*-
# encoding: utf-8

'''
Description: Seg P4M VI tif and get mean values
Author: yulu_ye16@163.com
'''

import numpy as np
import rasterio
import os
import warnings
from multiprocessing import Pool

def bands_combine(bands_path):
    os.chdir(bands_path)
    red = rasterio.open(r"result_Red.tif").read(1)
    green = rasterio.open(r"result_Green.tif").read(1)
    blue = rasterio.open(r"result_Blue.tif").read(1)
    rededge = rasterio.open(r"result_Rededge.tif").read(1)
    nir_raster = rasterio.open(r"result_Nir.tif")
    nir = nir_raster.read(1)

    out_img = "bands5.tif"
    out_meta = nir_raster.meta.copy()
    out_meta.update({"count": 5})

    file_list = [blue, green, red, rededge, nir]
    with rasterio.open(out_img, 'w', **out_meta) as dest:
        for band_nr, src in enumerate(file_list, start=1):
            dest.write(src, band_nr)

def remove_soil(in_tif, out_path, nmcari_threshold = 0.03):
    with rasterio.open(in_tif) as src:
        raster = src.read()
        profile = src.profile
        with np.errstate(divide='ignore', invalid='ignore'):
            B = raster[0]
            G = raster[1]
            R = raster[2]
            RE = raster[3]
            NIR = raster[4]

            mcari = ((RE - R) - 0.2 * (RE - G)) * (RE / R)
            nmcari = (mcari - np.nanmin(mcari)) / (np.nanmax(mcari) - np.nanmin(mcari))
            new_B = np.ma.masked_where(nmcari < nmcari_threshold, B).filled(np.nan)
            new_G = np.ma.masked_where(nmcari < nmcari_threshold, G).filled(np.nan)
            new_R = np.ma.masked_where(nmcari < nmcari_threshold, R).filled(np.nan)
            new_RE = np.ma.masked_where(nmcari < nmcari_threshold, RE).filled(np.nan)
            new_NIR = np.ma.masked_where(nmcari < nmcari_threshold, NIR).filled(np.nan)

            dst_img = os.path.join(out_path, 'masked_soil.tif')

            with rasterio.open(dst_img, mode='w', **profile) as dst:
                dst.write(new_R, 1)
                dst.write(new_G, 2)
                dst.write(new_B, 3)
                dst.write(new_RE, 4)
                dst.write(new_NIR, 5)
                dst.close()


def VisGeneration(in_path):
    in_file = os.path.join(in_path, 'masked_soil.tif')
    out_path = os.path.join(in_path, "VI")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    with rasterio.open(in_file) as src:
        raster = src.read()
        profile = src.profile
        with np.errstate(divide='ignore', invalid='ignore'):
            B = raster[0]
            G = raster[1]
            R = raster[2]
            RE = raster[3]
            NIR = raster[4]

            NDVI = (NIR - R) / (NIR + R)
            BNDVI = (NIR - B) / (NIR + B)
            GNDVI = (NIR - G) / (NIR + G)
            REGNDVI = (RE - G) / (RE + G)
            CVI = (NIR / G) * (R / G)
            GCI = (NIR / G) - 1
            GRVI = (G - R) / (G + R)
            NDRE = (NIR - RE) / (NIR + RE)
            LCI = (NIR - RE) / (NIR - R)
            MTCI = (NIR - RE) / (NIR - R)
            OSAVI = (1 + 0.16) * (NIR - R) / (NIR + R + 0.16)
            MCARI = ((RE - R) - 0.2 * (RE - G)) * (RE / R)
            RVI = NIR / R
            WDRVI = (0.2*NIR - R) / (0.2*NIR + R)
            TNDVI = ((NDVI+0.5)**0.5)
            SAVI = 1.5*(NIR - R) / (NIR + R + 0.5)
            EVI = 2.5*(NIR - R)/(1 + NIR - 2.4*R)
            RDVI = (NIR - R) / ((NIR + R)**0.5)
            TCARI = 3 * ((RE - R) - 0.2 * (RE - G) * (RE / R))
            SIPI = (NIR - B) / (NIR - R)
            CI_R = (NIR / R) - 1
            CI_RE = (NIR / RE) - 1
            DVI = NIR - R
            GOSAVI = (NIR - G) / (NIR + G + 0.16)
            NDREI = (RE - G) / (RE + G)
            NAVI = 1 - R / NIR
            S_CCCI = NDRE / NDVI
            TCARI_OSAVI = TCARI / OSAVI

            print("开始写入文件！")

        VIslist = ("B", "G", "R", "RE", "NIR",
                   "NDVI", "BNDVI", "GNDVI", "REGNDVI",
                   "CVI", "GCI", "GRVI", "NDRE", "LCI",
                   "MTCI", "OSAVI", "MCARI","RVI", "WDRVI",
                   "TNDVI", "SAVI", "EVI", "RDVI", "TCARI",
                   "SIPI", "CI_R", "CI_RE","DVI", "GOSAVI",
                   "NDREI", "NAVI", "S_CCCI", "TCARI_OSAVI")

        profile.update(dtype=NIR.dtype, count=1)
        for i in VIslist:
            outfile = os.path.join(out_path, i + ".tif")
            with rasterio.open(outfile, mode='w', **profile) as dst:
                dst.write(eval(i), 1)
                dst.close()
            print(i + " finished!")


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    date = "20220627"
    in_path = "F:/yeyulu/0.DATA/2022LF/P4M" + "/" + date
    # os.chdir(in_path)
    # bands_combine(bands_path=in_path)  #波段合并
    # in_tif = os.path.join(in_path, "bands5.tif")
    # remove_soil(in_tif=in_tif, out_path=in_path, nmcari_threshold = 0.06)  #土壤剔除
    VisGeneration(in_path)  #植被指数计算

    #######  多核  ######
    # date_list = ["F:/yeyulu/0.DATA/2021LF/P4M/20210704",
    #              "F:/yeyulu/0.DATA/2021LF/P4M/20210708",
    #              "F:/yeyulu/0.DATA/2021LF/P4M/20210716",
    #              "F:/yeyulu/0.DATA/2021LF/P4M/20210720",
    #              "F:/yeyulu/0.DATA/2021LF/P4M/20210724"]
    # for i in date_list:
    #     #in_tif = os.path.join(i, "bands5.tif")
    #     # bands_combine(bands_path=i)  #波段合并
    #     #remove_soil(in_tif=in_tif, out_path=i, nmcari_threshold=0.03)  # 土壤剔除
    #     VisGeneration(i)
    # # pool = Pool(len(date_list))
    # # pool.map(bands_combine, date_list)
    # # pool.close()
    # # pool.join()
    #   print(i + " finished!")
