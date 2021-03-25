import sys
from osgeo import gdal
import numpy as np
import cv2
import psycopg2
import pandas as pd
import os
import json
import requests


sys.path.append('/home/edel/PycharmProjects/anotador')

from data_annotator.cvmodel import build_cvred

def create_square(center, window_size=64):
    """
    Crea un cuadrado segun la resolucion de entrada, con centro en el punto dado
    :param center: tuple, center point
    :param window_size: int, size of the window
    :return: points: list, lista con los puntos de los 4 vertices del cuadrado
    """
    offset = window_size // 2
    x = center[0]
    y = center[1]
    points = [(x - offset, y - offset), (x + offset, y - offset), (x + offset, y + offset), (x - offset, y + offset)]
    return points


def load_image_geotif(filename, new_size=None):
    '''
    Carga una imagen Tiff,
    params: filename: string, nombre del fichero
            new_size: tamano de la imagen, si es None se carga con el tamano original, en otro caso se realiza el resize
    retorna el nump array de la image, la proyeccion y la geotransformacion
    '''
    ds = gdal.Open(filename)
    proj = ds.GetProjection()
    gt = ds.GetGeoTransform()
    tarjet_shape = np.zeros((3,), dtype=int)
    if new_size is None:
        tarjet_shape[0] = ds.RasterYSize
        tarjet_shape[1] = ds.RasterXSize
        tarjet_shape[2] = ds.RasterCount
    else:
        tarjet_shape[0] = new_size[1]
        tarjet_shape[1] = new_size[0]
        tarjet_shape[2] = ds.RasterCount - 1

    out_img = np.zeros(tarjet_shape, dtype=float)

    i = 0
    for k in range(1, ds.RasterCount + 1):
        band = ds.GetRasterBand(k)

        if k != 8:
            x = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, tarjet_shape[1], tarjet_shape[0]).astype('float')
            out_img[:, :, i] = x[:, :]
            i = i + 1

    return out_img, proj, gt


def save_image_geotif(filename, Array, GeoT, Projection, DataType):
    '''
    crea un fichero geotiff a partir de un arreglo numpy
    '''
    shape = np.shape(Array)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    DataSet = gtiff_driver.Create(filename, shape[0], shape[1], shape[2], DataType)
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection)
    for k in range(1, shape[2] + 1):
        data = Array[:, :, k-1]
        out_band = DataSet.GetRasterBand(k)
        out_band.WriteArray(data)
        DataSet.FlushCache()

    for k in range(1, shape[2] + 1):
        DataSet.GetRasterBand(k).ComputeStatistics(False)
        DataSet.BuildOverviews("average", [2, 4, 8, 16, 32])

    del DataSet


def Ganadora(lista):
    valor = np.amax(lista)
    if valor > 0.5:
        ind = np.where(lista == valor)
        return ind[0][0]
    else:
        return -1


def clasif_image(model, img, colors):
    shape = np.shape(img)
    overlay = np.zeros([shape[0], shape[1], 3], dtype=np.uint8)
    window_size = 32
    offset = window_size // 2
    x_list = []
    y_list = []
    b_list = []
    # shape[1] - offset):
    for py in range(offset, 120):
        print(py)
        for px in range(offset, shape[0] - offset):
                x = img[py - offset:py + offset, px - offset:px + offset]
                x = cv2.resize(x, (120, 120)) / 255.

                b_list.append(x)
                x_list.append(px)
                y_list.append(py)

                if len(b_list) == 10240:
                    batch_x = np.array(b_list)
                    predictions = model.predict(batch_x)

                    for pred, x, y in zip(predictions, x_list, y_list):
                        lab = Ganadora(pred)

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
            lab = Ganadora(pred)

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
    macro_project_id = '4'
    project_id = '8'
    image_date = '20200813'
    project_data_path = '/media/edel/Work/Projects_data/'
    input_image = 'texture_features.tif'
    drones_path = project_data_path + 'images/' + project_id + '/drones/' + image_date + '/' + input_image
    output_image = 'classification.tif'
    classify_path = project_data_path + 'images/' + project_id + '/drones/' + image_date + '/' + output_image
    input_checkpoint = 'model-checkpoints/20201022-063458/CVRED_weights.205-0.14.hdf5'
    checkpoint_path = project_data_path + 'macro_projects_data/' + macro_project_id + '/' + project_id + '/drones/' + image_date + '/' + input_checkpoint
    input_class_indices = 'model-checkpoints/20201022-063458/CVRED_class_indices.json'
    class_indices_path = project_data_path + 'macro_projects_data/' + macro_project_id + '/' + project_id + '/drones/' + image_date + '/' + input_class_indices

    with open(class_indices_path) as f:
        class_indices = json.load(f)

    nclass = len(class_indices)

    model = build_cvred(input_shape=(120, 120, 6), n_output_classes=nclass)
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

    image_array, proj, gt = load_image_geotif(image_path)




if __name__ == "__main__":
    main()


