from osgeo import gdal
import numpy as np
from anotador import settings
import cv2

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


def convert_to_byte(index_array):
    max_val = 1
    min_val = -1
    distance = max_val - min_val
    factor = round(255 / distance, 2)
    out_put = (index_array - min_val) * factor
    out_put = np.around(out_put, 0)
    out_put = out_put.astype(np.uint8)
    return out_put


def save_rgb_iv(path, iv_array, iv_name, raster_x_size, raster_y_size, gp, gt):
    gtiff_driver = gdal.GetDriverByName('GTiff')
    byte_array = convert_to_byte(iv_array)
    color_array = cv2.applyColorMap(byte_array, cv2.COLORMAP_JET)

    out_name = iv_name + '.tif'
    out_ds = gtiff_driver.Create(path + out_name, raster_x_size, raster_y_size, 3, gdal.GDT_Byte)

    out_ds.SetGeoTransform(gt)
    out_ds.SetProjection(gp)

    out_ds.GetRasterBand(1).WriteArray(color_array[:, :, 2])
    out_ds.FlushCache()

    out_ds.GetRasterBand(2).WriteArray(color_array[:, :, 1])
    out_ds.FlushCache()

    out_ds.GetRasterBand(3).WriteArray(color_array[:, :, 0])
    out_ds.FlushCache()

    for i in range(1, 4):
        out_ds.GetRasterBand(i).ComputeStatistics(False)
        out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])


def create_iv(path, checked_iv_list):
    input_file = path + 'sentinel.tif'
    output_file = path + 'iv.tif'

    try:
        ds = gdal.Open(input_file)
        gtiff_driver = gdal.GetDriverByName('GTiff')
        raster_x_size = ds.RasterXSize
        raster_y_size = ds.RasterYSize

        out_ds = gtiff_driver.Create(output_file, raster_x_size, raster_y_size, 16, gdal.GDT_Float32)
        gp = ds.GetProjection()
        gt = ds.GetGeoTransform()
        out_ds.SetProjection(gp)
        out_ds.SetGeoTransform(gt)

        band = ds.GetRasterBand(1)
        blue = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(2)
        green = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(3)
        red = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(4)
        vnir1 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(5)
        vnir2 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(6)
        vnir3 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(7)
        vnir4 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(8)
        vnir5 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(9)
        swir1 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(10)
        swir3 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)
        band = ds.GetRasterBand(11)
        swir4 = band.ReadAsArray(0, 0, raster_x_size, raster_y_size)

        # (B8-B4)/(B8+B4)
        # Indice de Vegetacion de Deferencia Normalizada
        ndvi = (vnir4 - red) / (np.where((vnir4 + red) == 0., np.nan, (vnir4 + red)))
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(ndvi)
        out_band.SetNoDataValue(0.0)

        # 2.5*((B8-B4)/(B8+ 6*B4 -7.5*B2 + 1))
        # Indice de Vegetación Mejorado (EVI)
        evi = (2.5 * vnir4 - red) / np.where(vnir4 + 6.0 * red - 7.5 * blue + 1.0 == 0., np.nan,
                                             vnir4 + 6.0 * red - 7.5 * blue + 1.0)
        out_band = out_ds.GetRasterBand(2)
        out_band.WriteArray(evi)
        out_band.SetNoDataValue(0.0)

        # B11/B8
        # Indice de Estrés Hídrico (MSI)
        msi = swir3 / np.where(vnir4 == 0., 0., vnir4)
        out_band = out_ds.GetRasterBand(3)
        out_band.WriteArray(msi)
        out_band.SetNoDataValue(0.0)

        # (B8-B11)/(B8+B11)
        # Indice de Diferencia Normalizada de Humedad (NDMI)
        ndmi = (vnir4 - swir3) / np.where(vnir4 + swir3 == 0., np.nan, vnir4 + swir3)
        out_band = out_ds.GetRasterBand(4)
        out_band.WriteArray(ndmi)
        out_band.SetNoDataValue(0.0)

        # (B3-B8)/(B3+B8)
        # Indice de Diferencial de Agua Normalizado (NDWI)
        ndwi = (green - vnir4) / np.where(green + vnir4 == 0., np.nan, green + vnir4)
        out_band = out_ds.GetRasterBand(5)
        out_band.WriteArray(ndwi)
        out_band.SetNoDataValue(0.0)

        # (B8-B4)/(B8+B4+0.428)*(1.428)
        # Indice de Vegetación Ajustado al Suelo (SAVI)
        savi = (vnir4 - red) / np.where((vnir4 + red + 0.428) * 1.428 == 0., np.nan, (vnir4 + red + 0.428) * 1.428)
        out_band = out_ds.GetRasterBand(6)
        out_band.WriteArray(savi)
        out_band.SetNoDataValue(0.0)

        # B5 / (B5+B11)
        # Indice de Area Foliar (LAI)
        lai = vnir1 / np.where(vnir1 + swir3 == 0., np.nan, vnir1 + swir3)
        out_band = out_ds.GetRasterBand(7)
        out_band.WriteArray(lai)
        out_band.SetNoDataValue(0.0)

        # (B9/B3)-1
        # Indice de Clorofila (GCI)
        gci = (swir1 - 1) / np.where(green == 0., np.nan, green - 1.0)
        out_band = out_ds.GetRasterBand(8)
        out_band.WriteArray(gci)
        out_band.SetNoDataValue(0.0)

        # (B8-B2) / (B8-B4)
        # Indice de Pigmentación Insensible a la Estructura (SIPI)
        sipi = (vnir4 - blue) / np.where(vnir4 - red == 0., np.nan, vnir4 - red)
        out_band = out_ds.GetRasterBand(9)
        out_band.WriteArray(sipi)
        out_band.SetNoDataValue(0.0)

        # Indice de Amarillez de la Vegetación (YVIMSS)
        yvimss = -0.899 * blue + 0.428 * red + 0.076 * vnir1 - 0.041 * vnir4
        out_band = out_ds.GetRasterBand(10)
        out_band.WriteArray(yvimss)
        out_band.SetNoDataValue(0.0)

        # (B8-B3)/(B8+B3)
        # Indice de Diferencia Normalizada de Verde (GNDVI)
        gndvi = (vnir4 - green) / np.where(vnir4 + green == 0., np.nan, vnir4 + green)
        out_band = out_ds.GetRasterBand(11)
        out_band.WriteArray(gndvi)

        # (B11+B4)-(B8+B2)/(B11+B4)+(B8+B2)
        # Indice de Suelo Desnudo (BSI)
        bsi = (swir3 + red) - (vnir4 + blue) / np.where((swir3 + red) + (vnir4 + blue) == 0., np.nan,
                                                        (swir3 + red) + (vnir4 + blue))
        out_band = out_ds.GetRasterBand(12)
        out_band.WriteArray(bsi)
        out_band.SetNoDataValue(0.0)

        # Indice de Hojas Verdes (GLI)
        gli = (2 * green - red - blue) / np.where(2 * green + red + blue == 0., np.nan,
                                                  2 * green + red + blue)
        out_band = out_ds.GetRasterBand(13)
        out_band.WriteArray(gli)
        out_band.SetNoDataValue(0.0)

        # Indice Triangular de Clorofila (TCI)
        tci = np.where((red == 0.), 0.,
                       (1.2 * (vnir1 - green) - 1.5 * (red - green) * np.sqrt(vnir1 / (red + 0.00000001))))
        out_band = out_ds.GetRasterBand(14)
        out_band.WriteArray(tci)
        out_band.SetNoDataValue(0.0)

        # (B8-B12)/(B8+B12)
        # Indice de Calcinación Normalizado (NBRI)
        nbri = (vnir4 - swir4) / np.where(vnir4 + swir4 == 0., np.nan, vnir4 + swir4)
        out_band = out_ds.GetRasterBand(15)
        out_band.WriteArray(nbri)
        out_band.SetNoDataValue(0.0)

        # (B8-B12)/(B8+B12)
        # Indice de Vegetación de Diferencia Normalizado Mejorado (ENDVI)
        endvi = (vnir4 + green) - (2.0 * blue) / np.where((vnir4 + green) + (2.0 * blue) == 0., np.nan,
                                                          (vnir4 + green) + (2.0 * blue))
        out_band = out_ds.GetRasterBand(16)
        out_band.WriteArray(endvi)
        out_band.SetNoDataValue(0.0)

        out_ds.FlushCache()
        for k in range(1, 17):
            out_ds.GetRasterBand(k).ComputeStatistics(False)
        out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
        del out_ds

        for i, iv in enumerate(checked_iv_list):
            #  1
            if iv == 'ndvi':
                save_rgb_iv(path, ndvi, iv, raster_x_size, raster_y_size, gp, gt)
            #  2
            if iv == 'evi':
                save_rgb_iv(path, evi, iv, raster_x_size, raster_y_size, gp, gt)
            #  3
            if iv == 'msi':
                save_rgb_iv(path, msi, iv, raster_x_size, raster_y_size, gp, gt)
            #  4
            if iv == 'ndmi':
                save_rgb_iv(path, ndmi, iv, raster_x_size, raster_y_size, gp, gt)
            #  5
            if iv == 'ndwi':
                save_rgb_iv(path, ndwi, iv, raster_x_size, raster_y_size, gp, gt)
            #  6
            if iv == 'savi':
                save_rgb_iv(path, savi, iv, raster_x_size, raster_y_size, gp, gt)
            #  7
            if iv == 'lai':
                save_rgb_iv(path, lai, iv, raster_x_size, raster_y_size, gp, gt)
            #  8
            if iv == 'gci':
                save_rgb_iv(path, gci, iv, raster_x_size, raster_y_size, gp, gt)
            #  9
            if iv == 'sipi':
                save_rgb_iv(path, sipi, iv, raster_x_size, raster_y_size, gp, gt)
            #  10
            if iv == 'yvimss':
                save_rgb_iv(path, yvimss, iv, raster_x_size, raster_y_size, gp, gt)
            #  11
            if iv == 'gndvi':
                save_rgb_iv(path, gndvi, iv, raster_x_size, raster_y_size, gp, gt)
            #  12
            if iv == 'bsi':
                save_rgb_iv(path, bsi, iv, raster_x_size, raster_y_size, gp, gt)
            #  13
            if iv == 'gli':
                save_rgb_iv(path, gli, iv, raster_x_size, raster_y_size, gp, gt)
            #  14
            if iv == 'tci':
                save_rgb_iv(path, tci, iv, raster_x_size, raster_y_size, gp, gt)
            #  15
            if iv == 'nbri':
                save_rgb_iv(path, nbri, iv, raster_x_size, raster_y_size, gp, gt)
            #  16
            if iv == 'endvi':
                save_rgb_iv(path, endvi, iv, raster_x_size, raster_y_size, gp, gt)

        status = "OK"
    except:
        status = "Error"

    return status
