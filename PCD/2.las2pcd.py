#!/usr/bin/env python
# coding:utf-8

'''
  Description: Seg las cloud points
  Author: yulu_ye16@163.com
  注：切换python py36环境使用
'''

import os.path
import numpy as np
import laspy
from pclpy import pcl

def find_files(input_directory, processed_files):
    files = os.listdir(input_directory)
    file_names = []
    for f in files:
        if f.endswith(
                ".las") and f not in processed_files:
            file_names.append(f)
    return (file_names)

# las读取转为 pcd的cloud形式，保留 XYZ及rgb
def las2pcd(file,save_path,name):
    las = laspy.read(file)
    inFile = np.vstack((las.x, las.y, las.z, las.intensity)).transpose()
    rgb = np.vstack((las.red, las.green, las.blue)).transpose()
    cloud = pcl.PointCloud.PointXYZRGBA().from_array(np.array(inFile, dtype=np.float32),rgb)
    address = os.path.join(save_path, name + ".pcd")
    pcl.io.savePCDFileASCII(address,cloud)
    return address

if __name__ == "__main__":
    las_path = r"F:\yeyulu\0.DATA\2021HN\3D\20211224\plots"
    processed_files = []
    num_filtered = 1
    file_names = find_files(las_path,processed_files)
    for i in range(len(file_names)):
        in_file = os.path.join(las_path, file_names[i])
        las2pcd(in_file, las_path, file_names[i].split(".")[0])