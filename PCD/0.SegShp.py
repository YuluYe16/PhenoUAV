#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Description: Seg shp
  Author: yulu_ye16@163.com
'''

import os
import shapefile
import shutil

if __name__ == '__main__':
    wd_path = 'F:/yeyulu/biomass'
    date = '20220705'
    mapBasePolyShpFile = os.path.join(wd_path, date, 'RGB/shp_3d/samples.shp')
    # 目标文件 夹 存放地址
    folderPolyAimMap = os.path.join(wd_path, date, 'RGB/shp_3d/seg')
    # 原文件的投影地址
    projectionFile = os.path.join(wd_path, date, 'RGB/shp_3d/samples.prj')

    print('Start...')
    rPolyShp = shapefile.Reader(mapBasePolyShpFile)
    for numFlag in range(rPolyShp.numRecords):
        fileName = rPolyShp.record(numFlag).plot_id
        # 目标Shp文件地址
        aimPolyMap = fr'{folderPolyAimMap}\{fileName}.shp'
        wPolyShp = shapefile.Writer(target=aimPolyMap, shapeType=5)
        # 添加名为'Size'的浮点型，6位有效，2位小数点的字段
        wPolyShp.field('plot_id', 'C', "10")

        # 读取原文件第一个要素的线点集
        # 添加异常处理，以防存在空Shp文件
        try:
            baseLinkPoint = [[list(i) for i in rPolyShp.shape(numFlag).points]]
        except IndexError:
            shutil.copy(projectionFile, f'{aimPolyMap[:-4]}.prj')
            continue
        # 将线点集写入到面点集中
        wPolyShp.poly(baseLinkPoint)

        # 写入plot_id信息
        wPolyShp.record(fileName)

        # 关闭写文件
        wPolyShp.close()

        shutil.copy(projectionFile, f'{aimPolyMap[:-4]}.prj')
        print(numFlag, '已经完成')
    print('End...')


