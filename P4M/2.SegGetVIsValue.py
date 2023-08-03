# -*- coding: utf-8 -*-
# encoding: utf-8

'''
Description: Seg P4M VI tif and get values
Author: yulu_ye16@163.com
'''

from osgeo import gdal
import rasterio
from rasterio.mask import mask
import geopandas
import numpy as np
import pandas as pd
import os
import shutil
import warnings
from tqdm import trange
from multiprocessing import Pool

def find_files(input_directory, processed_files):
    files = os.listdir(input_directory)
    file_names = []
    for f in files:
        if f.endswith(
                ".tif") and f not in processed_files:
            file_names.append(f)
    return (file_names)


def seg_tif(input_raster, input_shape, output_raster):
    rasterdata = rasterio.open(input_raster)
    shp = geopandas.read_file(input_shape)
    for i in range(len(shp)):
        geo = shp['geometry'][i]
        feature = [geo.__geo_interface__]
        out_img, out_transform = mask(rasterdata, feature,
                                      all_touched=True,
                                      crop=True,
                                      nodata=-1998)
        out_meta = rasterdata.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_img.shape[1],
                         "width": out_img.shape[2],
                         "transform": out_transform,
                         "crs": rasterdata.crs})
        with rasterio.open(os.path.join(output_raster, shp['plot_id'][i] + ".tif"), "w", **out_meta) as dest:
            dest.write(out_img)

def get_tif_mean(tif_path,excel_path,index_name):
    tif_list = os.listdir(tif_path)
    list_sorted = sorted(tif_list,key=lambda x: (
                             int(x.split('R')[1].split('_')[0]),
                             int(x.split('C')[1].split('.')[0]))
                         )
    out_df = pd.DataFrame()
    for i in list_sorted:
        vi_path = os.path.join(tif_path,i)
        arr = gdal.Open(vi_path).ReadAsArray()
        arr[np.where((arr == -1998) | (arr == 0))] = np.nan
        new = pd.DataFrame({'plot_id': i.split('.', 1)[0],
                            index_name: np.nanmean(arr)
                            }, index=[0]
                           )
        #out_df = out_df.append(new, ignore_index=True)
        out_df = pd.concat([out_df, new],axis=0)
    out_df.to_excel(os.path.join(excel_path, index_name + ".xlsx"), index=False)

def main(wd,date):
    #wd = r'F:\yeyulu\0.DATA\2021LF\P4M'
    wd_path = os.path.join(wd, date)
    os.chdir(wd_path)
    input_directory = os.path.join(wd_path)
    vi_path = os.path.join(input_directory, 'VI')
    input_shape = os.path.join(wd, 'shp', 'all.shp')  # 1.samples  2.all_plots

    seg_path = os.path.join(input_directory, "cotton_seg")
    if not os.path.exists(seg_path):
        os.makedirs(seg_path)
    excel_path = os.path.join(input_directory, "res_cotton")
    if not os.path.exists(excel_path):
        os.makedirs(excel_path)

    processed_files = []
    flag = True
    while flag:
        file_names = find_files(vi_path, processed_files)
        if len(file_names) > 0:
            for i in trange(len(file_names), position=0):
                in_file = os.path.join(vi_path, file_names[i])

                index_name = file_names[i].split(".")[0]
                output_raster = os.path.join(seg_path, index_name)
                if not os.path.exists(output_raster):
                    os.makedirs(output_raster)

                seg_tif(in_file, input_shape, output_raster)
                get_tif_mean(output_raster,excel_path,index_name)

                processed_files.append(file_names[i])  # append the processed file to the list
        else:
            flag = False
    print(date + " VI extraction finished!")

    df_empty = pd.DataFrame()
    index_list = os.listdir(excel_path)
    col = 0
    for filename in index_list:
        file_path = os.path.join(excel_path,filename)
        df = pd.read_excel(file_path)
        if col < 1:
            df_empty = pd.concat([df_empty, df], axis = 1)
        else:
            df_empty = pd.concat([df_empty,df.loc[:,df.columns!="plot_id"]], axis=1)
        col += 1
    df_empty.to_excel(os.path.join(input_directory, wd ,date+"_vi.xlsx"), index=False)

    os.chdir(wd_path)
    shutil.rmtree(input_directory + "/cotton_seg")
    shutil.rmtree(excel_path)
    print("Complete! Clear process files finished!")

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    wd = r'P4M'
    date = "20220627"
    main(wd, date)
    #items = ["20210704", "20210708", "20210716", "20210720","20210724"]
    # pool = Pool(len(items))
    # pool.map(main, items)
    # pool.close()
    # pool.join()
