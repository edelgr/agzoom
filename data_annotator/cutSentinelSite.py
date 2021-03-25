'''
Toma el listado de muestras puntuales por clase, es decir las coordenadas (x, y) marcadas sobre la imagen Sentinel mapa,
y las proyecta a coordenadas geograficas del sistema de coordenadas de la imagen (proyeccion de la imagen) y despues
se lleva a las coordenadas de pixeles (px, py). Despues considerando este punto el centro de la muestra de extrae una
subimagen del tamanno deseado
'''
from osgeo import ogr, osr, gdal
import os
import numpy as np
import psycopg2
import geopandas as gpd
import struct
from anotador import settings
from data_annotator.geoFunctions import BoundingBox1, transform_points

project_data_path = settings.MEDIA_ROOT


def cut_sentinel_site(path, project_id, project_name, image_date):
    sentinel_path = path + 'spectral_features.tif'
    mask_path = path + 'cloud_mask.tif'

    window_size = 7

    connection = None
    try:
        database_ = settings.DATABASES['default']['NAME']
        user_ = settings.DATABASES['default']['USER']
        password_ = settings.DATABASES['default']['PASSWORD']
        host_ = settings.DATABASES['default']['HOST']
        port_ = settings.DATABASES['default']['PORT']

        connection = psycopg2.connect(database=database_, user=user_, password=password_, host=host_, port=port_)

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)

    sql = 'select label_name, point as geom, site_name ' + \
          'from data_annotator_site as m, data_annotator_label as l ' + \
          'where m.sample_project_id=' + project_id + 'and m.label_id = l.id'

    gdf_site = gpd.read_postgis(sql, connection)

    gtiff_driver = gdal.GetDriverByName('GTiff')

    ds0 = gdal.Open(mask_path)
    ds1 = gdal.Open(sentinel_path)

    proj = ds1.GetProjection()
    gt = ds1.GetGeoTransform()

    target = osr.SpatialReference(wkt=proj)
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source, target)


    targetPath = project_data_path + 'dataset'
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath = project_data_path + 'dataset/' + project_name
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath = project_data_path + 'dataset/' + project_name + '/sentinel'
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath = project_data_path + 'dataset/' + project_name + '/sentinel/' + image_date
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    i = 0
    ptos_list = []
    for pn, name, label_name in list(zip(gdf_site['geom'], gdf_site['site_name'], gdf_site['label_name'])):
        print("Name: %s   label: %s" % (name, str(label_name)))
        pto = np.array(pn)
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(pto[0], pto[1])
        point.Transform(transform)
        pto1 = point.GetPoints()
        # Convert geographic coordinates to pixel coordinates
        center = transform_points(ds1, pto1, img2geo=False)
        print(center[0])

        px = center[0][0]
        py = center[0][1]

        # # Extract pixel value
        # band = ds0.GetRasterBand(1)
        # try:
        #    structval = band.ReadRaster(px, py, 1, 1, buf_type=gdal.GDT_Byte)
        # except OSError:
        #     print("Error leyendo el pto")
        #
        # result = struct.unpack('B', structval)[0]

        # if result == band.GetNoDataValue() or result == 255:
        #     i = i + 1
        #     print('muestra sobre nube: ', str(i))
        #     continue

        ulx, xres, xskew, uly, yskew, yres = gt

        lrx = ulx + (ds1.RasterXSize * xres)
        lry = uly + (ds1.RasterYSize * yres)

        pto = np.array([ulx, uly])
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(pto[0], pto[1])
        point.Transform(transform)
        pto1 = point.GetPoints()
        # Convert geographic coordinates to pixel coordinates
        center = transform_points(ds1, pto1, img2geo=False)
        print(center[0])
        ulx = center[0][0]
        uly = center[0][1]

        pto = np.array([lrx, lry])
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(pto[0], pto[1])
        point.Transform(transform)
        pto1 = point.GetPoints()
        # Convert geographic coordinates to pixel coordinates
        center = transform_points(ds1, pto1, img2geo=False)
        print(center[0])
        lrx = center[0][0]
        lry = center[0][1]
        if px < ulx + window_size // 2 or px > lrx - window_size // 2 or py < uly + window_size // 2 or py > lry - window_size // 2:
            print('rechazado')
            continue

        if center[0] not in ptos_list:
            ptos_list.append(center[0])
            square = BoundingBox1(center[0], window_size)
            targetClassPath = targetPath + '/' + label_name
            try:
                os.mkdir(targetClassPath)
            except OSError:
                pass

            outputPath = targetClassPath + "/" + name + ".tif"
            out_ds = gtiff_driver.Create(outputPath, window_size, window_size, ds1.RasterCount,
                                         ds1.GetRasterBand(1).DataType)
            out_gt = list(gt)
            offsets = gdal.ApplyGeoTransform(gt, square[0][0], square[0][1])
            out_gt[0] = offsets[0]
            out_gt[3] = offsets[1]

            out_ds.SetProjection(proj)
            out_ds.SetGeoTransform(out_gt)

            for i in range(1, ds1.RasterCount + 1):
                band = ds1.GetRasterBand(i)
                data = band.ReadAsArray(square[0][0], square[0][1], window_size, window_size)

                out_band = out_ds.GetRasterBand(i)
                out_band.WriteArray(data)

                del data
                out_ds.FlushCache()
            del out_ds

    if connection:
        connection.close()
        print("PostgreSQL connection is closed \n")
