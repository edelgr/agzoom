from os import listdir
from os.path import isfile
import numpy as np
import cv2
from osgeo import ogr, osr, gdal
from data_annotator.geoFunctions import transform_points
from anotador import settings

project_data_path = settings.MEDIA_ROOT


def CreateRasterSpectralFeatures(bands, output_file, envelopes):
    """
    :param bands: A list with the names of every input channel
    :param output_file: A string with the name of the output file
    :return: A single raster which contains all the input bands
    """
    first_band_name = bands[0]
    first_band = gdal.Open(first_band_name)
    gt = first_band.GetGeoTransform()
    proj = first_band.GetProjection()

    target = osr.SpatialReference(wkt=proj)
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source, target)

    minx = min(envelopes[0], envelopes[2], envelopes[4], envelopes[6])
    maxx = max(envelopes[0], envelopes[2], envelopes[4], envelopes[6])
    miny = min(envelopes[1], envelopes[3], envelopes[5], envelopes[7])
    maxy = max(envelopes[1], envelopes[3], envelopes[5], envelopes[7])

    pto1 = np.array((minx, maxy))
    point1 = ogr.Geometry(ogr.wkbPoint)
    point1.AddPoint(pto1[0], pto1[1])
    point1.Transform(transform)
    point1 = point1.GetPoints()
    # Convert geographic coordinates to pixel coordinates
    p1 = transform_points(first_band, point1, img2geo=False)
    x1 = p1[0][0]
    y1 = p1[0][1]

    pto2 = np.array((maxx, miny))
    point2 = ogr.Geometry(ogr.wkbPoint)
    point2.AddPoint(pto2[0], pto2[1])
    point2.Transform(transform)
    point2 = point2.GetPoints()
    # Convert geographic coordinates to pixel coordinates
    p2 = transform_points(first_band, point2, img2geo=False)
    x2 = p2[0][0]
    y2 = p2[0][1]

    raster_x_size = abs(x2 - x1)
    raster_y_size = abs(y2 - y1)

    # Xgeo = GT(0) + Xpixel * GT(1) + Yline * GT(2)
    # Ygeo = GT(3) + Xpixel * GT(4) + Yline * GT(5)
    #
    # In case of north up images, the  GT(2) and GT(4) coefficients  are  zero, and the
    # GT(1) is pixel width, and GT(5) is pixel height.The(GT(0), GT(3)) position is the
    # top left corner of the top left pixel of the raster.

    out_gt = list(gt)
    offsets = gdal.ApplyGeoTransform(gt, x1, y1)
    out_gt[0] = offsets[0]
    out_gt[3] = offsets[1]

    gt = tuple(out_gt)

    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(output_file + '.tif', raster_x_size, raster_y_size, 11, gdal.GDT_Int16)
    out_ds.SetProjection(proj)
    out_ds.SetGeoTransform(gt)

    gtiff_driver1 = gdal.GetDriverByName('GTiff')
    out_ds1 = gtiff_driver1.Create(output_file + '_color.tif', raster_x_size, raster_y_size, 3, gdal.GDT_Byte)
    out_ds1.SetProjection(proj)
    out_ds1.SetGeoTransform(gt)

    del first_band

    contrats = -0.35
    brightness = 7.0

    # 1 Azul 10m
    band_blue = bands[0]
    ds = gdal.Open(band_blue)
    band = ds.GetRasterBand(1)
    blue = band.ReadAsArray(x1, y1, raster_x_size, raster_y_size)
    norm_blue = cv2.normalize(blue, None, alpha=contrats, beta=brightness,
                              norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    norm_blue = np.clip(norm_blue, 0, 1)
    norm_blue = (255 * norm_blue).astype(np.uint8)

    # 2 Verde 10m
    band_green = bands[1]
    ds = gdal.Open(band_green)
    band = ds.GetRasterBand(1)
    green = band.ReadAsArray(x1, y1, raster_x_size, raster_y_size)
    norm_green = cv2.normalize(green, None, alpha=contrats, beta=brightness,
                               norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    norm_green = np.clip(norm_green, 0, 1)
    norm_green = (255 * norm_green).astype(np.uint8)

    # 3 rojo 10m
    band_red = bands[2]
    ds = gdal.Open(band_red)
    band = ds.GetRasterBand(1)
    red = band.ReadAsArray(x1, y1, raster_x_size, raster_y_size)
    norm_red = cv2.normalize(red, None, alpha=contrats, beta=brightness,
                             norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    norm_red = np.clip(norm_red, 0, 1)
    norm_red = (255 * norm_red).astype(np.uint8)

    # 4 Visible e Infrarrojo Cercano (B05 VNIR1 20m)
    band_nir1 = bands[3]
    ds = gdal.Open(band_nir1)
    band = ds.GetRasterBand(1)
    vnir1 = band.ReadAsArray(x1 // 2, y1 // 2, raster_x_size // 2, raster_y_size // 2)
    resized_vnir1 = cv2.resize(vnir1, (raster_x_size, raster_y_size))

    # 5 Visible e Infrarrojo Cercano (B06 VNIR2 20m)
    band_nir2 = bands[4]
    ds = gdal.Open(band_nir2)
    band = ds.GetRasterBand(1)
    vnir2 = band.ReadAsArray(x1 // 2, y1 // 2, raster_x_size // 2, raster_y_size // 2)
    resized_vnir2 = cv2.resize(vnir2, (raster_x_size, raster_y_size))

    # 6 Visible e Infrarrojo Cercano (B07 VNIR3 20m)
    band_nir3 = bands[5]
    ds = gdal.Open(band_nir3)
    band = ds.GetRasterBand(1)
    vnir3 = band.ReadAsArray(x1 // 2, y1 // 2, raster_x_size // 2, raster_y_size // 2)
    resized_vnir3 = cv2.resize(vnir3, (raster_x_size, raster_y_size))

    # 7 Visible e Infrarrojo Cercano (B08 VNIR4 10m)
    band_nir4 = bands[6]
    ds = gdal.Open(band_nir4)
    band = ds.GetRasterBand(1)
    vnir4 = band.ReadAsArray(x1, y1, raster_x_size, raster_y_size)

    # 8 Visible e Infrarrojo Cercano (B8A VNIR5 20m)
    band_nir5 = bands[7]
    ds = gdal.Open(band_nir5)
    band = ds.GetRasterBand(1)
    vnir5 = band.ReadAsArray(x1 // 2, y1 // 2, raster_x_size // 2, raster_y_size // 2)
    resized_vnir5 = cv2.resize(vnir5, (raster_x_size, raster_y_size))

    # 9 Onda Corta Infrarroja (B09 SWIR1 60m)
    band_swr1 = bands[8]
    ds = gdal.Open(band_swr1)
    band = ds.GetRasterBand(1)
    swr1 = band.ReadAsArray(x1 // 6, y1 // 6, raster_x_size // 6, raster_y_size // 6)
    resized_swr1 = cv2.resize(swr1, (raster_x_size, raster_y_size))

    # 10 Onda Corta Infrarroja (SWIR3 20m)
    band_swr3 = bands[9]
    ds = gdal.Open(band_swr3)
    band = ds.GetRasterBand(1)
    swr3 = band.ReadAsArray(x1 // 2, y1 // 2, raster_x_size // 2, raster_y_size // 2)
    resized_swr3 = cv2.resize(swr3, (raster_x_size, raster_y_size))

    # 11 Onda Corta Infrarroja (SWIR4 20m)
    band_swr4 = bands[10]
    ds = gdal.Open(band_swr4)
    band = ds.GetRasterBand(1)
    swr4 = band.ReadAsArray(x1 // 2, y1 // 2, raster_x_size // 2, raster_y_size // 2)
    resized_swr4 = cv2.resize(swr4, (raster_x_size, raster_y_size))

    # Escribiendo la imagen
    out_ds.GetRasterBand(1).WriteArray(blue)
    out_ds.GetRasterBand(2).WriteArray(green)
    out_ds.GetRasterBand(3).WriteArray(red)
    out_ds.GetRasterBand(4).WriteArray(resized_vnir1)
    out_ds.GetRasterBand(5).WriteArray(resized_vnir2)
    out_ds.GetRasterBand(6).WriteArray(resized_vnir3)
    out_ds.GetRasterBand(7).WriteArray(vnir4)
    out_ds.GetRasterBand(8).WriteArray(resized_vnir5)
    out_ds.GetRasterBand(9).WriteArray(resized_swr1)
    out_ds.GetRasterBand(10).WriteArray(resized_swr3)
    out_ds.GetRasterBand(11).WriteArray(resized_swr4)

    out_ds.FlushCache()
    for k in range(1, 12):
        out_ds.GetRasterBand(k).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds

    # Escribiendo la  composicion a color natural
    out_ds1.GetRasterBand(1).WriteArray(norm_red)
    out_ds1.GetRasterBand(2).WriteArray(norm_green)
    out_ds1.GetRasterBand(3).WriteArray(norm_blue)

    out_ds1.FlushCache()
    for k in range(1, 4):
        out_ds1.GetRasterBand(k).ComputeStatistics(False)
    out_ds1.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds1


def spectral_features(processing_dir_path, image_path, envelopes):
    """
    Prepara los caminos donde se encuentran los canales espectrales de la iamgen sentinel
    que seran recortados para el ROI (envelopes)
    Se extraen las siguientes bandas Sentinel 2 (S2A_MSIL1C y S2A_MSIL2A)
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
    processing_dir_path: path donde estan todas las imagenes asociada a una fecha
    image_path: imagen en formato sentinel .SAVE
    envelopes: lista de los puntos del rectangulo
    """
    b02 = b03 = b04 = b05 = b06 = b07 = b08 = b8a = b09 = b11 = b12 = None
    path1 = path2 = path3 = None
    name = None
    if image_path[4:10] == 'MSIL2A':
        path1 = processing_dir_path + image_path + '/R10m'
    if image_path[4:10] == 'MSIL1C':
        path1 = processing_dir_path + image_path

    files1 = [f for f in listdir(path1) if isfile(path1 + '/' + f)]
    for i in range(len(files1)):
        if image_path[4:10] == 'MSIL2A':
            name = files1[i][-10:-8]
        if image_path[4:10] == 'MSIL1C':
            name = files1[i][-6:-4]
        if name == '02':
            b02 = path1 + "/" + files1[i]
        if name == '03':
            b03 = path1 + "/" + files1[i]
        if name == '04':
            b04 = path1 + "/" + files1[i]
        if name == '08':
            b08 = path1 + "/" + files1[i]

    if image_path[4:10] == 'MSIL2A':
        path2 = processing_dir_path + image_path + '/R20m'
    if image_path[4:10] == 'MSIL1C':
        path2 = processing_dir_path + image_path

    files2 = [f for f in listdir(path2) if isfile(path2 + '/' + f)]
    for i in range(len(files2)):
        if image_path[4:10] == 'MSIL2A':
            name = files2[i][-10:-8]
        if image_path[4:10] == 'MSIL1C':
            name = files2[i][-6:-4]
        if name == '05':
            b05 = path2 + "/" + files2[i]
        if name == '06':
            b06 = path2 + "/" + files2[i]
        if name == '07':
            b07 = path2 + "/" + files2[i]
        if name == '8A':
            b8a = path2 + "/" + files2[i]
        if name == '11':
            b11 = path2 + "/" + files2[i]
        if name == '12':
            b12 = path2 + "/" + files2[i]

    if image_path[4:10] == 'MSIL2A':
        path3 = processing_dir_path + image_path + '/R60m'
    if image_path[4:10] == 'MSIL1C':
        path3 = processing_dir_path + image_path

    files3 = [f for f in listdir(path3) if isfile(path3 + '/' + f)]
    for i in range(len(files3)):
        if image_path[4:10] == 'MSIL2A':
            name = files3[i][-10:-8]
        if image_path[4:10] == 'MSIL1C':
            name = files3[i][-6:-4]
        if name == '09':
            b09 = path3 + "/" + files3[i]

    files_bands = [b02, b03, b04, b05, b06, b07, b08, b8a, b09, b11, b12]
    output_file = processing_dir_path + "sentinel"
    CreateRasterSpectralFeatures(files_bands, output_file, envelopes)
