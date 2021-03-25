'''
Toma el listado de muestras puntuales por clase, es decir las coordenadas (x, y) marcadas sobre la imagen de Drones mapa,
y las proyecta a coordenadas geograficas del sistema de coordenadas de la imagen (proyeccion de la imagen) y despues
se lleva de las coordenadas de pixeles (px, py). Despues considerando este punto el centro de la muestra de extrae una
subimagen del tamanno deseado
'''
from osgeo import ogr, osr, gdal
import os
import numpy as np
import psycopg2
import geopandas as gpd
from data_annotator import clasificator
from data_annotator.geoFunctions import BoundingBox1, transform_points, load_image_geotif
from anotador import settings

project_data_path = settings.MEDIA_ROOT


def cut_drones_site(project_id, project_name, image_date, image_name):
    drones_path = project_data_path + 'images/' + project_name + '/drones/' + image_date + '/' + image_name

    window_size = 16

    connection = None
    try:
        database_ = "anotadordb"
        user_ = "postgres"
        password_ = "postgres"
        host_ = "127.0.0.1"
        port_ = "5432"

        connection = psycopg2.connect(database=database_, user=user_, password=password_, host=host_, port=port_)

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)

    sql = 'select label_name, point as geom, site_name ' + \
          'from data_annotator_site as m, data_annotator_label as l ' + \
          'where m.sample_project_id=' + project_id + 'and m.label_id = l.id'

    gdf_site = gpd.read_postgis(sql, connection)

    gtiff_driver = gdal.GetDriverByName('GTiff')

    ds1 = gdal.Open(drones_path)

    proj = ds1.GetProjection()
    gt = ds1.GetGeoTransform()

    target = osr.SpatialReference(wkt=proj)
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source, target)

    targetPath = project_data_path + 'dataset/' + project_name
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath = project_data_path + 'dataset/' + project_name + '/drones'
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath = project_data_path + 'dataset/' + project_name + '/drones/' + image_date
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    img_width, img_height = ds1.RasterXSize, ds1.RasterYSize

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

        x = center[0][0]
        y = center[0][1]
        off = (window_size // 2)

        if (x <= off) or (x >= img_width - off) or (y <= off) or (y >= img_height - off):
            print("x : ", x)
            print("img_width : ", img_width)
            print("y : ", y)
            print("img_height : ", img_height)
            print("off : ", off)
            continue

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


def cla_drones_site(project_name, image_date, label_name, image_name):
    drones_path = project_data_path + 'images/' + project_name + '/drones/' + image_date + '/' + image_name
    targetPath = project_data_path + 'dataset/' + project_name + '/drones/' + image_date

    image_array, proj, gt = load_image_geotif(drones_path)

    path_rf = targetPath + '/' + label_name + '/' + 'Clasificador/canna_rf.xml'

    print(path_rf)

    clasificator.ClasificarRF(image_array, path_rf)


if __name__ == "__main__":
    project_name = '1-Cultuvos Varios Cabaiguan - Neiva'
    image_date = '20200720'
    # cut_drones_site(project_id, image_date, 'natural_color.tif')
    cla_drones_site(project_name, image_date, 'natural_color.tif')
