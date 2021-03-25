from osgeo import gdal
from os import listdir
from os.path import isfile, join
import numpy as np
import cv2
import math

from anotador import settings
project_data_path = settings.MEDIA_ROOT

'''
Sentinel 2
B1  -  60 m  -  443 nm     - Ultra azul (costa y aerosol)
B2  -  10 m  -  490 nm     - Azul 
B3  -  10 m  -  560 nm     - Verde 
B4  -  10 m  -  665 nm     - Rojo 
B5  -  20 m  -  705 nm     - Visible e Infrarrojo Cercano (VNIR1) 
B6  -  20 m  -  740 nm     - Visible e Infrarrojo Cercano (VNIR2)  
B7  -  20 m  -  783 nm     - Visible e Infrarrojo Cercano (VNIR3)  
B8  -  10 m  -  842 nm     - Visible e Infrarrojo Cercano (VNIR4)  
B8A -  20 m  -  865 nm     - Visible e Infrarrojo Cercano (VNIR5) 
B9  -  60 m  -  940 nm     - Onda Corta Infrarroja (SWIR1) 
B10 -  60 m  -  1375 nm    - Onda Corta Infrarroja (SWIR2) 
B11 -  20 m  -  1610 nm    - Onda Corta Infrarroja (SWIR3) 
B12 -  20 m  -  2190 nm    - Onda Corta Infrarroja (SWIR4) 
'''
'''
Se crea una imagen GeoTiff con los siguientes canales:
B2  -  10 m  -  490 nm     - Azul 
B3  -  10 m  -  560 nm     - Verde 
B4  -  10 m  -  665 nm     - Rojo 
B5  -  10 m  -  705 nm     - Visible e Infrarrojo Cercano (VNIR1) 
B8  -  10 m  -  842 nm     - Visible e Infrarrojo Cercano (VNIR4)  
B8A -  10 m  -  865 nm     - Visible e Infrarrojo Cercano (VNIR5) 
B11 -  10 m  -  1610 nm    - Onda Corta Infrarroja (SWIR3)
I1  -  10 m  -  ndvi       - Indice de Vegetacion de Diferencia Normalizada
I2  -  10 m  -  ndwi       - Indice Agua de Diferencia Normalizada
I3  -  10 m  -  savi       - Indice de Vegetacion Ajustado al Suelo
I4  -  10 m  -  slavi      - Indice de Area folial
I5  -  10 m  -  tci        - Indice de triangular de clorofila
I6  -  10 m  -  gli        - Indice de Hojas Verdes
I7  -  10 m  -  yvismss    - Indice de amarillez de la vegetacion
'''

import os

def create_spectralfeatures(path):
    input_file = path + 'sentinel.tif'
    output_file = path + 'spectral_features.tif'

    if os.path.isfile(output_file):
        os.remove(output_file)

    ds = gdal.Open(input_file)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    raster_x_size = ds.RasterXSize
    raster_y_size = ds.RasterYSize
    out_ds = gtiff_driver.Create(output_file, raster_x_size, raster_y_size, 14, gdal.GDT_Byte)
    out_ds.SetProjection(ds.GetProjection())
    out_ds.SetGeoTransform(ds.GetGeoTransform())

    # 1 Azul
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

    # 4 Visible e Infrarrojo Cercano (VNIR1)
    band = ds.GetRasterBand(4)
    vnir1 = band.ReadAsArray().astype('float64')
    norm_vnir1 = np.zeros(np.shape(vnir1))
    norm_vnir1 = cv2.normalize(vnir1, norm_vnir1, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(4)
    out_band.WriteArray(norm_vnir1)

    # 5 Visible e Infrarrojo Cercano (VNIR4)
    band = ds.GetRasterBand(7)
    vnir4 = band.ReadAsArray().astype('float64')
    norm_vnir4 = np.zeros(np.shape(vnir4))
    norm_vnir4 = cv2.normalize(vnir4, norm_vnir4, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(5)
    out_band.WriteArray(norm_vnir4)

    # 6 Visible e Infrarrojo Cercano (VNIR5)
    band = ds.GetRasterBand(8)
    vnir5 = band.ReadAsArray().astype('float64')
    norm_vnir5 = np.zeros(np.shape(vnir5))
    norm_vnir5 = cv2.normalize(vnir5, norm_vnir5, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(6)
    out_band.WriteArray(norm_vnir5)

    # 7 Onda Corta Infrarroja (SWIR3)
    band = ds.GetRasterBand(10)
    swir3 = band.ReadAsArray().astype('float64')
    norm_swir3 = np.zeros(np.shape(swir3))
    norm_swir3 = cv2.normalize(swir3, norm_swir3, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(7)
    out_band.WriteArray(norm_swir3)

    # (B8-B4)/(B8+B4)
    # 8 Indice de Vegetacion de Diferencia Normalizada (NDVI)
    ndvi = (vnir4 - red) / (np.where((vnir4 + red) == 0., np.nan, (vnir4 + red)))
    norm_ndvi = np.zeros(np.shape(ndvi))
    norm_ndvi = cv2.normalize(ndvi, norm_ndvi, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(8)
    out_band.WriteArray(norm_ndvi)

    # (B3-B8)/(B3+B8)
    # 9 Indice de Diferencial de Agua Normalizado (NDWI)
    ndwi = (green - vnir4) / np.where(green + vnir4 == 0., np.nan, green + vnir4)
    norm_ndwi = np.zeros(np.shape(ndwi))
    norm_ndwi = cv2.normalize(ndwi, norm_ndwi, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(9)
    out_band.WriteArray(norm_ndwi)

    # (B8-B4)/(B8+B4+0.428)*(1.428)
    # 10 Indice de Vegetación Ajustado al Suelo (SAVI)
    savi = (vnir4 - red) / np.where((vnir4 + red + 0.428) * 1.428 == 0., np.nan, (vnir4 + red + 0.428) * 1.428)
    norm_savi = np.zeros(np.shape(savi))
    norm_savi = cv2.normalize(savi, norm_savi, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(10)
    out_band.WriteArray(norm_savi)

    # B5 / (B5+B11)
    # 11 Indice de Area Foliar (LAI)
    slavi = vnir1 / np.where(vnir1 + swir3 == 0., np.nan, vnir1 + swir3)
    norm_slavi = np.zeros(np.shape(slavi))
    norm_slavi = cv2.normalize(slavi, norm_slavi, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(11)
    out_band.WriteArray(norm_slavi)

    # Indice de Hojas Verdes (GLI)
    gli = (2 * green - red - blue) / np.where(2 * green + red + blue == 0., np.nan,
                                              2 * green + red + blue)
    norm_gli = np.zeros(np.shape(gli))
    norm_gli = cv2.normalize(gli, norm_gli, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(12)
    out_band.WriteArray(norm_gli)

    # Indice Triangular de Clorofila (TCI)
    tci = np.where((red == 0.), 0.,
                   (1.2 * (vnir1 - green) - 1.5 * (red - green) * np.sqrt(vnir1 / (red + 0.00000001))))
    norm_tci = np.zeros(np.shape(tci))
    norm_tci = cv2.normalize(tci, norm_tci, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(13)
    out_band.WriteArray(norm_tci)

    # Indice de Amarillez de la Vegetación (YVIMSS)
    yvimss = -0.899 * blue + 0.428 * red + 0.076 * vnir1 - 0.041 * vnir4
    norm_yvimss = np.zeros(np.shape(yvimss))
    norm_yvimss = cv2.normalize(yvimss, norm_yvimss, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    out_band = out_ds.GetRasterBand(14)
    out_band.WriteArray(norm_yvimss)

    out_ds.FlushCache()
    for k in range(1, 15):
        out_ds.GetRasterBand(k).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds
