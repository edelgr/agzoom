from osgeo import gdal
from os import listdir
from os.path import isfile, join
import numpy as np
import cv2
import math
# Local Binary Pattern function
from skimage.feature import local_binary_pattern
from anotador import settings

project_data_path = settings.MEDIA_ROOT


'''
Drones
- Azul 
- Verde 
- Rojo 

'''
'''
Se crea una imagen GeoTiff con los siguientes canales:
- Azul 
- Verde 
- Rojo 
- Azul LBP
- Verde LBP
- Rojo  LBP
'''


def CreateRasterTextureFeatures(filename, output_file):
    """
    :param bands: A list with the names of every input channel
    :param output_file: A string with the name of the output file
    :return: A single raster which contains all the input bands
    """
    firstBandName = filename
    firstBand = gdal.Open(firstBandName)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    RasterXSize = firstBand.RasterXSize
    RasterYSize = firstBand.RasterYSize
    out_ds = gtiff_driver.Create(output_file, RasterXSize, RasterYSize, 6, gdal.GDT_Byte)
    out_ds.SetProjection(firstBand.GetProjection())
    out_ds.SetGeoTransform(firstBand.GetGeoTransform())
    del firstBand

    # 1 Azul
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    blue = band.ReadAsArray().astype('float64')
    norm_blue = np.zeros(np.shape(blue))
    norm_blue = cv2.normalize(blue, norm_blue, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(norm_blue)

    # 2 Verde
    band = ds.GetRasterBand(2)
    green = band.ReadAsArray().astype('float64')
    norm_green = np.zeros(np.shape(green))
    norm_green = cv2.normalize(green, norm_green, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(2)
    out_band.WriteArray(norm_green)

    # 3 rojo
    band = ds.GetRasterBand(3)
    red = band.ReadAsArray().astype('float64')
    norm_red = np.zeros(np.shape(red))
    norm_red = cv2.normalize(red, norm_red, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(3)
    out_band.WriteArray(norm_red)

    # 4 Azul LBP
    radius = 3
    # Number of points to be considered as neighbourers
    no_points = 8 * radius
    # Uniform LBP is used
    lbp = local_binary_pattern(blue, no_points, radius, method='uniform')
    out_band = out_ds.GetRasterBand(4)
    out_band.WriteArray(lbp)

    # 5 Verde LBP
    radius = 3
    # Number of points to be considered as neighbourers
    no_points = 8 * radius
    # Uniform LBP is used
    lbp = local_binary_pattern(green, no_points, radius, method='uniform')
    out_band = out_ds.GetRasterBand(5)
    out_band.WriteArray(lbp)

    # 5 Rojo LBP
    radius = 3
    # Number of points to be considered as neighbourers
    no_points = 8 * radius
    # Uniform LBP is used
    lbp = local_binary_pattern(red, no_points, radius, method='uniform')
    out_band = out_ds.GetRasterBand(6)
    out_band.WriteArray(lbp)

    del red
    del green
    del blue
    del lbp

    out_ds.FlushCache()
    for k in range(1, 7):
        out_ds.GetRasterBand(k).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds


def texture_features(project_id, image_date):
    processing_image_path = project_data_path + 'images/' + project_id + '/drones/' + image_date + '/natural_color.tif'
    output_file = project_data_path + 'images/' + project_id + '/drones/' + image_date + '/texture_features.tif'
    CreateRasterTextureFeatures(processing_image_path, output_file)

if __name__ == '__main__':
    project_id_list = ['8']
    image_date_list = ['20200813']

    i = 0
    for project, date in zip(project_id_list, image_date_list):
        i = i + 1
        print(i)
        texture_features(project, date)
