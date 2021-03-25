from osgeo import gdal
import numpy as np
from anotador import settings

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

def create_ripe(path):
    input_file = path + 'sentinel.tif'
    output_file = path + 'ripe.tif'

    if os.path.isfile(output_file):
        os.remove(output_file)

    ds = gdal.Open(input_file)
    if ds is None:
        return
    gtiff_driver = gdal.GetDriverByName('GTiff')
    raster_x_size = ds.RasterXSize
    raster_y_size = ds.RasterYSize
    out_ds = gtiff_driver.Create(output_file, raster_x_size, raster_y_size, 3, gdal.GDT_Byte)
    out_ds.SetProjection(ds.GetProjection())
    out_ds.SetGeoTransform(ds.GetGeoTransform())

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
    # Indice de Vegetacion de Diferencia Normalizada (NDVI)
    ndvi = (vnir4 - red) / (np.where((vnir4 + red) == 0., np.nan, (vnir4 + red)))

    # 2.5*((B8-B4)/(B8+ 6*B4 -7.5*B2 + 1))
    # Indice de Vegetación Mejorado (EVI)
    evi = (2.5 * vnir4 - red) / np.where(vnir4 + 6.0 * red - 7.5 * blue + 1.0 == 0., np.nan,
                                         vnir4 + 6.0 * red - 7.5 * blue + 1.0)

    # B11/B8
    # Indice de Estrés Hídrico (MSI)
    msi = swir3 / np.where(vnir4 == 0., 0., vnir4)

    # (B8-B11)/(B8+B11)
    # Indice de Diferencia Normalizada de Humedad (NDMI)
    ndmi = (vnir4 - swir3) / np.where(vnir4 + swir3 == 0., np.nan, vnir4 + swir3)

    # (B3-B8)/(B3+B8)
    # Indice de Diferencial de Agua Normalizado (NDWI)
    ndwi = (green - vnir4) / np.where(green + vnir4 == 0., np.nan, green + vnir4)

    # (B8-B4)/(B8+B4+0.428)*(1.428)
    # Indice de Vegetación Ajustado al Suelo (SAVI)
    savi = (vnir4 - red) / np.where((vnir4 + red + 0.428) * 1.428 == 0., np.nan, (vnir4 + red + 0.428) * 1.428)

    # B5 / (B5+B11)
    # Indice de Area Foliar (LAI)
    lai = vnir1 / np.where(vnir1 + swir3 == 0., np.nan, vnir1 + swir3)

    # (B9/B3)-1
    # Indice de Clorofila (GCI)
    gci = (swir1 - 1) / np.where(green == 0., np.nan, green - 1.0)

    # (B8-B2) / (B8-B4)
    # Indice de Pigmentación Insensible a la Estructura (SIPI)
    sipi = (vnir4 - blue) / np.where(vnir4 - red == 0., np.nan, vnir4 - red)

    # Indice de Amarillez de la Vegetación (YVIMSS)
    yvimss = -0.899 * blue + 0.428 * red + 0.076 * vnir1 - 0.041 * vnir4

    # (B8-B3)/(B8+B3)
    # Indice de Diferencia Normalizada de Verde (GNDVI)
    gndvi = (vnir4 - green) / np.where(vnir4 + green == 0., np.nan, vnir4 + green)

    # (B11+B4)-(B8+B2)/(B11+B4)+(B8+B2)
    # Indice de Suelo  Desnudo(BSI)
    nbri = (swir3 + red) - (vnir4 + blue) / np.where((swir3 + red) + (vnir4 + blue) == 0., np.nan,
                                                     (swir3 + red) + (vnir4 + blue))

    # Indice de Hojas Verdes (GLI)
    gli = (2 * green - red - blue) / np.where(2 * green + red + blue == 0., np.nan,
                                              2 * green + red + blue)

    # Indice Triangular de Clorofila (TCI)
    tci = np.where((red == 0.), 0.,
                   (1.2 * (vnir1 - green) - 1.5 * (red - green) * np.sqrt(vnir1 / (red + 0.00000001))))

    # (B8-B12)/(B8+B12)
    # Indice de Calcinación Normalizado (NBRI)
    nbri = (vnir4 - swir4) / np.where(vnir4 + swir4 == 0., np.nan, vnir4 + swir4)

    # (B8-B12)/(B8+B12)
    # Indice de Vegetación de Diferencia Normalizado Mejorado (ENDVI)
    endvi = (vnir4 + green) - (2.0 * blue) / np.where((vnir4 + green) + (2.0 * blue) == 0., np.nan,
                                                      (vnir4 + green) + (2.0 * blue))

    # cgndvi = np.where(gndvi < 0.33, 0, np.where((gndvi >= 0.35) and (gndvi < 0.5), 1,
    #                                             np.where((gndvi >= 0.5) and (gndvi < 0.55), 2, 3)))
    # cendvi = np.where(endvi < 0.33, 0, np.where((endvi >= 0.33) and (endvi < 0.5), 1,
    #                                             np.where((endvi >= 0.5) and (endvi < 0.6), 2, 3)))
    # cndvi = np.where(ndvi < 0.25, 0, np.where((ndvi >= 0.25) and (ndvi < 0.55), 1,
    #                                           np.where((ndvi >= 0.55) and (ndvi < 0.7), 2, 3)))
    # cndwi = np.where(ndwi < 0.4, 2, 1)
    # cyvimss = np.where(yvimss > 0.5, 2, 1)

    ripe_r = np.zeros(np.shape(endvi))
    ripe_g = np.zeros(np.shape(endvi))
    ripe_b = np.zeros(np.shape(endvi))

    for py in range(raster_y_size):
        print(py)
        for px in range(raster_x_size):
            lista = [0, 0, 0, 0]
            # lista[cgndvi[py][px]] += 1
            # lista[cendvi[py][px]] += 1
            # lista[cndvi[py][px]] += 1
            # lista[cndwi[py][px]] += 1
            # lista[cyvimss[py][px]] += 1
            if gndvi[py][px] < 0.35:
                lista[0] += 1
            else:
                if (gndvi[py][px] >= 0.35) and (gndvi[py][px] < 0.5):
                     lista[1] += 1
                else:
                    if (gndvi[py][px] >= 0.5) and (gndvi[py][px] < 0.55):
                        lista[2] += 1
                    else:
                        lista[3] += 1

            if endvi[py][px] < 0.33:
                lista[0] += 1
            else:
                if (endvi[py][px] >= 0.33) and (endvi[py][px] < 0.5):
                    lista[1] += 1
                else:
                    if (endvi[py][px] >= 0.5) and (endvi[py][px] < 0.6):
                        lista[2] += 1
                    else:
                        lista[3] += 1

            if ndvi[py][px] < 0.25:
                lista[0] += 1
            else:
                if (ndvi[py][px] >= 0.25) and (ndvi[py][px] < 0.55):
                    lista[1] += 1
                else:
                    if (ndvi[py][px] >= 0.55) and (ndvi[py][px] < 0.7):
                        lista[2] += 1
                    else:
                        lista[3] += 1

            if (ndwi[py][px] < 0.4):
                lista[2] += 1
            else:
                lista[1] += 1

            if (yvimss[py][px] > 0.5):
                lista[2] += 1
            else:
                lista[1] += 1

            c = np.argmax(lista)
            # suelo descubierto
            if c == 0:
                ripe_r[py][px] = 255
                ripe_g[py][px] = 255
                ripe_b[py][px] = 255
            # canna en crecimiento
            if c == 1:
                ripe_r[py][px] = 255
                ripe_g[py][px] = 165
                ripe_b[py][px] = 0
            # canna madura
            if c == 2:
                ripe_r[py][px] = 255
                ripe_g[py][px] = 255
                ripe_b[py][px] = 0
            # canna pasada de madura
            if c == 3:
                ripe_r[py][px] = 0
                ripe_g[py][px] = 255
                ripe_b[py][px] = 0

    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(ripe_r)
    out_band.SetNoDataValue(0)
    out_band = out_ds.GetRasterBand(2)
    out_band.WriteArray(ripe_g)
    out_band.SetNoDataValue(0)
    out_band = out_ds.GetRasterBand(3)
    out_band.WriteArray(ripe_b)
    out_band.SetNoDataValue(0)

    out_ds.FlushCache()
    for k in range(1, 4):
        out_ds.GetRasterBand(k).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds
