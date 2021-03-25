from osgeo import gdal
from anotador import settings
from os import listdir
from os.path import isfile, join
from data_annotator.S2PixelCloudDetector import S2PixelCloudDetector
from data_annotator.geoFunctions import GetGeoInfo, CreateGeoTiff
import numpy as np
import matplotlib.pyplot as plt

project_data_path = settings.MEDIA_ROOT

'''
Entrada
Sentinel 2
B2  -  10 m  -  490 nm     - Azul 
B3  -  10 m  -  560 nm     - Verde 
B4  -  10 m  -  665 nm     - Rojo 
B5  -  20 m  -  705 nm     - Visible e Infrarrojo Cercano (VNIR1) 
B6  -  20 m  -  740 nm     - Visible e Infrarrojo Cercano (VNIR2)  
B7  -  20 m  -  783 nm     - Visible e Infrarrojo Cercano (VNIR3)  
B8  -  10 m  -  842 nm     - Visible e Infrarrojo Cercano (VNIR4)  
B8A -  20 m  -  865 nm     - Visible e Infrarrojo Cercano (VNIR5) 
B9  -  60 m  -  940 nm     - Onda Corta Infrarroja (SWIR1)  
B11 -  20 m  -  1610 nm    - Onda Corta Infrarroja (SWIR3) 
B12 -  20 m  -  2190 nm    - Onda Corta Infrarroja (SWIR4) 
'''
import os
def plot_cloud_mask(mask, figsize=(15, 15), fig=None):
    """
    Utility function for plotting a binary cloud mask.
    """
    if fig == None:
        plt.figure(figsize=figsize)
    plt.imshow(mask)


def create_cloud_mask(path):
    input_file = path + 'sentinel.tif'
    output_file = path + "cloud_mask.tif"

    if os.path.isfile(output_file):
        os.remove(output_file)

    ds = gdal.Open(input_file)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    raster_x_size = ds.RasterXSize // 10
    raster_y_size = ds.RasterYSize // 10
    out_ds = gtiff_driver.Create(output_file, raster_x_size, raster_y_size, 3, gdal.GDT_Byte)
    out_ds.SetProjection(ds.GetProjection())
    out_ds.SetGeoTransform(ds.GetGeoTransform())

    scale_factor = 10000.0
    img_stack = np.zeros((raster_y_size, raster_x_size, 1, 10), dtype=np.float64)

    b01 = np.zeros([raster_y_size, raster_x_size], dtype=np.float64)
    b01 = np.expand_dims(b01, axis=2)
    img_stack[:, :, :, 0] = b01

    band = ds.GetRasterBand(1)
    b02 = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b02 = np.expand_dims(b02, axis=2)
    img_stack[:, :, :, 1] = (b02 / scale_factor)

    band = ds.GetRasterBand(3)
    b04 = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b04 = np.expand_dims(b04, axis=2)
    img_stack[:, :, :, 2] = b04 / scale_factor

    band = ds.GetRasterBand(4)
    b05 = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b05 = np.expand_dims(b05, axis=2)
    img_stack[:, :, :, 3] = b05 / scale_factor

    band = ds.GetRasterBand(7)
    b08 = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b08 = np.expand_dims(b08, axis=2)
    img_stack[:, :, :, 4] = b08 / scale_factor

    band = ds.GetRasterBand(8)
    b8A = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b8A = np.expand_dims(b8A, axis=2)
    img_stack[:, :, :, 5] = b8A / scale_factor

    band = ds.GetRasterBand(9)
    b09 = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b09 = np.expand_dims(b09, axis=2)
    img_stack[:, :, :, 6] = b09 / scale_factor

    b10 = np.zeros([raster_y_size, raster_x_size], dtype=np.float64)
    b10 = np.expand_dims(b10, axis=2)
    img_stack[:, :, :, 7] = b10

    band = ds.GetRasterBand(10)
    b11 = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b11 = np.expand_dims(b11, axis=2)
    img_stack[:, :, :, 8] = b11 / scale_factor

    band = ds.GetRasterBand(11)
    b12 = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, raster_x_size, raster_y_size).astype('float64')
    b12 = np.expand_dims(b12, axis=2)
    img_stack[:, :, :, 9] = b12 / scale_factor

    cloud_detector = S2PixelCloudDetector(threshold=0.95, average_over=4, dilation_size=2)
    cloud_masks = cloud_detector.get_cloud_masks(img_stack) * 255

    mask = np.zeros((cloud_masks.shape[0], cloud_masks.shape[1]), dtype=np.byte)
    mask[:, :] = cloud_masks[:, :, 0]

    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(mask)
    out_band.SetNoDataValue(0)
    out_band = out_ds.GetRasterBand(2)
    out_band.WriteArray(mask)
    out_band.SetNoDataValue(0)
    out_band = out_ds.GetRasterBand(3)
    out_band.WriteArray(mask)
    out_band.SetNoDataValue(0)

    out_ds.FlushCache()
    out_ds.GetRasterBand(1).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds



