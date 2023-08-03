#!/usr/bin/env python
# coding:utf-8

'''
  Description: Seg las cloud points
  Author: yulu_ye16@163.com
'''

import os
import whitebox

def find_files(input_directory, processed_files):
    files = os.listdir(input_directory)
    file_names = []
    for f in files:
        if f.endswith(
                ".shp") and f not in processed_files:  
            file_names.append(f)
    return (file_names)


def main(in_las,shp_path,out_path):
    wbt = whitebox.WhiteboxTools()
    wbt.set_verbose_mode(False)  
    input_directory = shp_path  
    output_directory = out_path  

    if os.path.isdir(output_directory) != True:  
        os.mkdir(output_directory)

    processed_files = []  
    num_filtered = 1  
    flag = True  
    while flag:
        file_names = find_files(input_directory,
                                processed_files)  
        if len(file_names) > 0:  
            for i in range(len(file_names)):
                in_file = os.path.join(input_directory, file_names[i])  
                out_file = os.path.join(output_directory, file_names[i].split(".")[0])+'_cloud.las'  
                print(out_file)
                print("Processing  LAS {} OF {} (total filtered = {})".format(i + 1, len(file_names),
                                                                              num_filtered))
                wbt.clip_lidar_to_polygon(
                    i=in_las,
                    polygons=in_file,
                    output=out_file
                )
                processed_files.append(file_names[i]) 
                num_filtered += 1  
        else:
            flag = False

    print("Complete")

if __name__ == '__main__':
    #date = '20220624'
    #wd_path = "biomass"
    in_las = r"cloud.las"
    shp_path = r"seg"
    out_path = r"plots"
    main(in_las, shp_path, out_path)

