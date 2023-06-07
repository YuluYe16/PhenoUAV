# -*- coding: utf-8 -*-
# encoding: utf-8

'''
  Description: calculate the plant height
  Author: yulu_ye16@163.com
'''

import rasterio
from rasterio.mask import mask
import geopandas
from PIL import Image
import numpy as np
import pandas as pd
import os
import shutil

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
    print("seg plots finished")

def get_ph(tif_path, out_path):
    os.chdir(tif_path)
    out_path = wd_path
    tif_list = sorted(os.listdir(tif_path))
    list_sorted = sorted(tif_list,
                         key=lambda x: (
                             int(x.split('R')[1].split('_')[0]),
                             int(x.split('C')[1].split('.')[0])
                         )
                         )
    out_df = pd.DataFrame()
    for i in list_sorted:
        im = Image.open(i)
        arr = np.array(im)
        arr[arr == -1998] = np.NaN
        new = pd.DataFrame({'plot_id': i.split('.', 1)[0],
                            'p1': np.nanpercentile(arr, 1),
                            'p2': np.nanpercentile(arr, 2),
                            'p95': np.nanpercentile(arr, 95),
                            'p98': np.nanpercentile(arr, 98),
                            }, index=[0]
                           )
        #out_df = out_df.append(new, ignore_index=True)
        out_df = pd.concat([out_df, new], axis=0)
    #out_df["P95-P1"] = (out_df["p95"] - out_df["p1"]) * 100
    #out_df["P98-P1"] = (out_df["p98"] - out_df["p1"]) * 100
    out_df.to_excel(os.path.join(out_path, date, 'T3.xlsx'), index=False)
    print("PH extraction finished!")

def main(date,wd_path):
    input_raster = os.path.join(wd_path, date, 'dsm.tif')
    input_shape = os.path.join(wd_path, 'shp_filter/all_3.shp')  # 1.samples  2.all_plots
    output_raster = os.path.join(wd_path, date, "tmp")
    if not os.path.exists(output_raster):
        os.makedirs(output_raster)
    seg_tif(input_raster, input_shape, output_raster)

    out_path = os.path.join(wd_path, date)
    get_ph(output_raster, out_path)

    os.chdir(wd_path)
    shutil.rmtree(output_raster)
    print("Complete! Clear process files finished!")

if __name__ == '__main__':

    wd_path = r'F:\yeyulu\XJ_results'
    main(date, wd_path)
