import sys
from osgeo import ogr, osr, gdal
import numpy as np
import cv2
import psycopg2
import pandas as pd
import json
import geopandas
from matplotlib import pyplot
from data_annotator.cvmodel import build_cvred

from data_annotator.geoFunctions import load_image_geotif, save_image_geotif

sys.path.append('/home/edel/PycharmProjects/anotador')


def ganadora(lista):
    valor = np.amax(lista)
    if valor > 0.5:
        ind = np.where(lista == valor)
        return ind[0][0]
    else:
        return -1


def inside(x, y, ds_image, ds_shp):
    xoff, a, b, yoff, d, e = ds_image.GetGeoTransform()
    xp = a * x + b * y + a * 0.5 + b * 0.5 + xoff
    yp = d * x + e * y + d * 0.5 + e * 0.5 + yoff

    # crs = osr.SpatialReference()
    # crs.ImportFromWkt(ds_image.GetProjectionRef())
    # # create lat/long crs with WGS84 datum
    # crsGeo = osr.SpatialReference()
    # crsGeo.ImportFromEPSG(4326)  # 4326 is the EPSG id of lat/long crs
    # t = osr.CoordinateTransformation(crs, crsGeo)
    # (lat, long, z) = t.TransformPoint(xp, yp)

    pt = ogr.Geometry(ogr.wkbPoint)
    pt.AddPoint(xp, yp)

    layer = ds_shp.GetLayer(0)
    layer.SetSpatialFilter(pt)

    for feature in layer:
        pepe = feature.items()
        return True
    return False


def clasif_parcels(model, img, ds_image, ds_shp, colors):
    shape = np.shape(img)
    overlay = np.zeros([shape[0], shape[1], 3], dtype=np.uint8)
    window_size = 7
    offset = window_size // 2
    x_list = []
    y_list = []
    b_list = []
    for py in range(offset, shape[1] - offset):
        for px in range(offset, shape[0] - offset):
            print(px, py)
            if inside(px, py, ds_image, ds_shp):
                x = img[py - offset:py + offset, px - offset:px + offset]
                x = cv2.resize(x, (120, 120)) / 255.

                b_list.append(x)
                x_list.append(px)
                y_list.append(py)

                if len(b_list) == 64:
                    batch_x = np.array(b_list)
                    predictions = model.predict(batch_x)

                    for pred, x, y in zip(predictions, x_list, y_list):
                        lab = ganadora(pred)

                        if lab != -1:
                            overlay[y, x, 0] = colors[lab][0]
                            overlay[y, x, 1] = colors[lab][1]
                            overlay[y, x, 2] = colors[lab][2]

                    b_list.clear()
                    x_list.clear()
                    y_list.clear()

    if len(b_list) > 0:
        batch_x = np.array(b_list)
        predictions = model.predict(batch_x)

        for pred, x, y in zip(predictions, x_list, y_list):
            lab = ganadora(pred)

            if lab != -1:
                overlay[y, x, 0] = colors[lab][0]
                overlay[y, x, 1] = colors[lab][1]
                overlay[y, x, 2] = colors[lab][2]

    overlay = cv2.medianBlur(overlay, 3)
    return overlay


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def main():
    macro_project_id = '1-clasificacion de cultivos varios'
    project_id = '1-Cultuvos Varios Cabaiguan - Neiva'
    image_date = '20200527'
    project_data_path = '/media/edel/Work/Projects_data/'
    input_image = 'area.tif'
    sentinel_path = project_data_path + 'processing_image/' + project_id + '/sentinel/' + image_date + '/' + input_image
    output_image = 'classification_parcels_total.tif'
    classify_path = project_data_path + 'processing_image/' + project_id + '/sentinel/' + image_date + '/' + output_image
    input_checkpoint = 'model-checkpoints/20201005-031716/CVRED_weights.197-0.45.hdf5'
    checkpoint_path = project_data_path + 'macro_projects_data/' + macro_project_id + '/sentinel/' + input_checkpoint
    input_class_indices = 'model-checkpoints/20201005-031716/CVRED_class_indices.json'
    class_indices_path = project_data_path + 'macro_projects_data/' + macro_project_id + '/sentinel/' + input_class_indices

    input_shp = 'Cultivos_Varios_region_new.shp'
    shape_in_path = project_data_path + 'shape_features/' + project_id + '/' + input_shp
    output_shp = 'Cultivos_Varios_region_new.shp'
    shape_out_path = project_data_path + 'shape_features/' + project_id + '/' + output_shp

    gdf = geopandas.read_file(shape_in_path)
    gdf.plot()
    pyplot.show()

    with open(class_indices_path) as f:
        class_indices = json.load(f)

    nclass = len(class_indices)

    model = build_cvred(input_shape=(120, 120, 16), n_output_classes=nclass)
    model.load_weights(checkpoint_path)

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

    sql = 'select color, label_name from data_annotator_label as l where l.macro_project_id=' + macro_project_id

    df_label = pd.read_sql(sql, connection)

    colors = []
    for ci in class_indices:
        for i, cla in enumerate(df_label['label_name']):
            if ci == cla:
                c = df_label['color'][i]
                colors.append(hex_to_rgb(c))
                break

    image_array, proj, gt = load_image_geotif(sentinel_path)

    ds_shp = ogr.Open(shape_in_path)
    ds_image = gdal.Open(sentinel_path)
    new_image_array = clasif_parcels(model, image_array, ds_image, ds_shp, colors)

    save_image_geotif(classify_path, new_image_array, gt, proj, gdal.GDT_Byte)


if __name__ == "__main__":
    main()
