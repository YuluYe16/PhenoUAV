#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Description: Seg tif
  Author: yulu_ye16@163.com
'''

import rasterio
from rasterio.mask import mask
import os
import geopandas
import warnings

def seg_tif(input_raster, input_shape, output_raster):
    '''
    按shp拆分小区
    '''
    rasterdata = rasterio.open(input_raster)
    shp = geopandas.read_file(input_shape)
    for i in range(len(shp)):
        geo = shp['geometry'][i]
        feature = [geo.__geo_interface__]
        out_img, out_transform = mask(rasterdata, feature,
                                      all_touched=True,
                                      crop=True, nodata=None)
        out_meta = rasterdata.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_img.shape[1],
                         "width": out_img.shape[2],
                         "transform": out_transform,
                         "crs": rasterdata.crs})
        with rasterio.open(output_raster + shp['plot_id'][i] + ".tif", "w", **out_meta) as dest:
            dest.write(out_img)
    print("seg finished")

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    wd_path = r'F:/yeyulu/0.DATA/2021HN/CC/'

    date = '20211211'
    input_raster = wd_path + date + '/result.tif'
    input_shape = wd_path + '/shp/cotton.shp'  # 1.samples  2.all_plots
    output_raster = wd_path + date +'/plots/'
    if not os.path.exists(output_raster):
        os.makedirs(output_raster)
    seg_tif(input_raster, input_shape, output_raster)
    print(date+" finished!")