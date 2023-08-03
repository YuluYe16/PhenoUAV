#!/usr/bin/env python
# coding:utf-8

'''
  Description: Seg las cloud points
  Author: yulu_ye16@163.com
  注：切换python py3.6 pclpy11环境使用
'''

import os
import open3d as o3d
import numpy as np
import pandas as pd
from scipy import spatial
import matplotlib.pyplot as plt
import alphashape
from descartes import PolygonPatch

def find_files(input_directory, processed_files):
    files = os.listdir(input_directory)
    file_names = []
    for f in files:
        if f.endswith(
                ".pcd") and f not in processed_files:
            file_names.append(f)
    return (file_names)

def slope_filter(cloud, step, eldif_thre=0.5, slope_thre=0.1):
    point_cloud = np.asarray(cloud.points)
    x_min, y_min, z_min = np.amin(point_cloud, axis=0)
    x_max, y_max, z_max = np.amax(point_cloud, axis=0)
    width = np.ceil((x_max - x_min) / step)
    height = np.ceil((y_max - y_min) / step)
    h = list()  
    for i in range(len(point_cloud)):

        col = np.ceil((point_cloud[i][0] - x_min) / step)
        row = np.ceil((point_cloud[i][1] - y_min) / step)
        h.append((row-1) * width + col)
    h = np.array(h)
    h_indice = np.argsort(h)  
    h_sorted = h[h_indice]
    ground_idx = []  
    begin = 0
    for i in range(len(h_sorted) - 1):
        if h_sorted[i] == h_sorted[i + 1]:
            continue
        else:
            point_idx = h_indice[begin: i + 1]
            z_value = point_cloud[[point_idx], 2]
            z_min_idx = np.argmin(z_value) 

            delth = point_cloud[[point_idx], 2] - point_cloud[[point_idx[z_min_idx]], 2] 
            deltx = point_cloud[[point_idx], 0] - point_cloud[[point_idx[z_min_idx]], 0]
            delty = point_cloud[[point_idx], 1] - point_cloud[[point_idx[z_min_idx]], 1]
            distances = np.sqrt(deltx * deltx + delty * delty)
            slope = np.divide(delth, distances, out=np.zeros_like(delth), where=distances != 0)
            for k in range(len(point_idx)):
                if (delth[0][k] > eldif_thre) & (slope[0][k] > slope_thre):
                    ground_idx.append(point_idx[k])

        begin = i + 1
    ground_points = (cloud.select_by_index(ground_idx))
    return ground_points

def main(input_pc,output):
    os.chdir(output)
    input_directory = input_pc
    output_directory = output
    processed_files = []
    num_filtered = 1
    flag = True
    out_df = pd.DataFrame(columns=("plot_id", "canopy_area", "canopy_volume"))
    while flag:
        file_name = find_files(input_directory,processed_files)
        file_names = sorted(file_name,
                             key=lambda x: (
                                 int(x.split('R')[1].split('_C')[0]),
                                 int(x.split('_C')[1].split('_cloud')[0])
                             )
                             )
        if len(file_names) > 0:
            for i in range(len(file_names)):
                in_file = os.path.join(input_directory, file_names[i])
                print("Processing  plots {} OF {} (total filtered = {})".format(i + 1, len(file_names),
                                                                              num_filtered))
                pcd = o3d.io.read_point_cloud(in_file)
                cl, ind = pcd.remove_statistical_outlier(nb_neighbors=5,
                                                         std_ratio=2.0)
                sor_cloud = pcd.select_by_index(ind)

                ######################################################################################################
                grid_step = 0.2  
                elevation_difference_threshold = 0.1  
                slope_threshold = 0.1  
                #####################################################################################################
                
                filtered_cloud = slope_filter(sor_cloud, grid_step, elevation_difference_threshold, slope_threshold)

                
                hull, idx = filtered_cloud.compute_convex_hull()

                area = hull.get_surface_area()  
                volume = hull.get_volume()  

                points = np.asarray(filtered_cloud.points)
                point2d = np.c_[points[:, 1], points[:, 2]]
                alpha_shape = alphashape.alphashape(point2d, 5)


                new = pd.DataFrame({'plot_id': file_names[i].split("_cloud")[0],
                                    'canopy_area': area,
                                    'canopy_volume': volume,
                                    'side_area': alpha_shape.area
                                    }, index=[0]
                                   )
                out_df = out_df.append(new, ignore_index=True)

                processed_files.append(file_names[i]) 
                num_filtered += 1  
        else:
            flag = False

        out_df.to_excel(os.path.join(output_directory, '3d_UAV.xlsx'), index=False)
    print("Complete!")

if __name__ == '__main__':

    input_pc = r"plots"
    output = r'20211224'
    main(input_pc, output)
