from osgeo import gdal
import tensorflow as tf
import sys
from packaging import version
import numpy as np

sys.path.append('/home/edel/PycharmProjects/anotador')

from data_annotator.cvmodel2 import build_cvred
from data_annotator.msi_image_generator import MsiImageDataGenerator


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def save_image_geotif(filename, Array, GeoT, Projection, DataType):
    '''
    crea un fichero geotiff a partir de un arreglo numpy
    '''
    shape = np.shape(Array)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    DataSet = gtiff_driver.Create(filename, shape[1], shape[0], shape[2], DataType)
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection)
    for k in range(1, shape[2] + 1):
        data = Array[:, :, k - 1]
        out_band = DataSet.GetRasterBand(k)
        out_band.WriteArray(data)
        DataSet.FlushCache()

    for k in range(1, shape[2] + 1):
        DataSet.GetRasterBand(k).ComputeStatistics(False)
        DataSet.BuildOverviews("average", [2, 4, 8, 16, 32])

    del DataSet


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
        tarjet_shape[2] = ds.RasterCount

    out_img = np.zeros(tarjet_shape, dtype=float)

    i = 0
    for k in range(1, ds.RasterCount + 1):
        band = ds.GetRasterBand(k)

        if k != 8:
            x = band.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, tarjet_shape[1], tarjet_shape[0]).astype('float')
            out_img[:, :, i] = x[:, :]
            i = i + 1

    return out_img, proj, gt


def ganadora(lista):
    valor = np.amax(lista)
    if valor > 0.0:
        ind = np.where(lista == valor)
        return ind[0][0]
    else:
        return -1


def clasif_image(model, image_array, window_size, bs, colors):
    shape = np.shape(image_array)
    # shape[0] filas shape[1] columnas
    n = shape[0] * shape[1]
    classify_datagen = MsiImageDataGenerator(rescale=1. / 255)
    dataset = classify_datagen.flow_from_image(image_array=image_array, target_size=(7, 7, 14), window_size=window_size,
                                               batch_size=bs)
    step_size = n // bs

    overlay = np.zeros([shape[0], shape[1], 3], dtype=np.uint8)

    predictions = model.predict(
        dataset,
        batch_size=None,
        verbose=0,
        steps=step_size,
        callbacks=None,
        max_queue_size=10,
        workers=1,
        use_multiprocessing=False)

    for index, pred in enumerate(predictions):
        y = index // shape[1]
        x = index % shape[1]
        lab = ganadora(pred)
        if lab != -1:
            overlay[y, x, 0] = colors[lab + 1][0]
            overlay[y, x, 1] = colors[lab + 1][1]
            overlay[y, x, 2] = colors[lab + 1][2]
        else:
            overlay[y, x, 0] = 0
            overlay[y, x, 1] = 0
            overlay[y, x, 2] = 0

    return overlay


# *******************************************************************************
def main():
    print("TensorFlow version: ", tf.__version__)
    assert version.parse(tf.__version__).release[0] >= 2, \
        "This code requires TensorFlow 2.0 or above."

    # cuda = tf.test.is_built_with_cuda()
    # gpus = tf.config.list_physical_devices('GPU')


    project_name = str(2) + '-' + "Azucar"
    plat = 'sentinel'
    project_data_path = '/media/edel/MyFiles1/edel/Project_data/'
    path = project_data_path + 'images/' + project_name
    ff = '20210301'
    dir_images = path + '/' + plat + '/' + ff + "/A/"
    image_path = dir_images + 'spectral_features.tif'

    image_array, proj, gt = load_image_geotif(image_path)

    project_data_path2 = '/media/edel/MyFiles1/edel/Project_data2/'
    checkpoint_path = project_data_path2 + 'dataset/model-checkpoints/20210321-030321/CVRED_weights.160-0.24.hdf5'

    model = build_cvred(input_shape=(7, 7, 14), n_output_classes=13)
    model.load_weights(checkpoint_path)

    output_image = 'classification.tif'
    classify_path = dir_images + output_image

    class_indices = [{"label": "Lagunas", "color": "#0A0CFF"},
                     {"label": "Arroz", "color": "#FBFF0F"},
                     {"label": "Boniato", "color": "#AF164B"},
                     {"label": "Ca\u00f1a de az\u00facar", "color": "#0CE5FF"},
                     {"label": "Frijoles", "color": "#FFBB82"},
                     {"label": "Hierba", "color": "#B5FFCE"},
                     {"label": "Maiz", "color": "#03FF0C"},
                     {"label": "Malanga", "color": "#FFD00F"},
                     {"label": "Pl\u00e1tano", "color": "#FF0000"},
                     {"label": "Suelo", "color": "#F6EAFF"},
                     {"label": "Tabaco tapado", "color": "#4F3D0E"},
                     {"label": "Frutales", "color": "#FF33B6"},
                     {"label": "Embalses y microembalses", "color": "#40F0FF"},
                     {"label": "Pastos naturales", "color": "#BCFF91"},
                     {"label": "Yuca", "color": "#16A017"},
                     {"label": "Cultivos varios", "color": "#A3FF79"},
                     {"label": "Apoyo a la producci\u00f3n agropecuaria", "color": "#FF0000"},
                     {"label": "Vivienda individual(unifamiliar)", "color": "#0A07D7"},
                     {"label": "Asentamientos poblacionales Rurales", "color": "#FFC247"},
                     {"label": "Caf\u00e9", "color": "#663B0A"},
                     {"label": "Pastos y forrajes cultivados", "color": "#7CFF5A"},
                     {"label": "Bosques naturales", "color": "#23A876"},
                     {"label": "Superficie ociosa", "color": "#F6FF2C"},
                     {"label": "Guayaba", "color": "#FFC144"},
                     {"label": "Naranja", "color": "#579057"},
                     {"label": "Cochiqueras", "color": "#FFE4D7"},
                     {"label": "Caminos", "color": "#FED5FF"},
                     {"label": "Ca\u00f1adas", "color": "#2383FF"},
                     {"label": "Latifolias", "color": "#BEFF4C"},
                     {"label": "\u00c1rea no apta", "color": "#FFE8C6"},
                     {"label": "R\u00edos", "color": "#1468FF"},
                     {"label": "Mango", "color": "#FFCF0A"},
                     {"label": "Albaricoque", "color": "#F6FFA0"},
                     {"label": "Frutabomba", "color": "#FFDD52"},
                     {"label": "Vaquer\u00edas", "color": "#FFE9D7"},
                     {"label": "Ajo", "color": "#F67EFF"},
                     {"label": "Terrapl\u00e9n", "color": "#81524C"},
                     {"label": "Man\u00ed", "color": "#705866"}]

    clases = ["Embalses y microembalses",
              "Arroz",
              "Boniato",
              "Bosques naturales",
              "Ca\u00f1a de az\u00facar",
              "Asentamientos poblacionales Rurales",
              "Frijoles",
              "Hierba",
              "Maiz",
              "Malanga",
              "Pl\u00e1tano",
              "Suelo",
              "Yuca"]

    colors = [(255, 255, 255)]
    for ci in clases:
        for i, cla in enumerate(class_indices):
            if cla["label"] == ci:
                c = cla["color"]
                colors.append(hex_to_rgb(c))
                break

    print(colors)
    window_size = 7
    bs = 8192
    new_image_array = clasif_image(model, image_array, window_size, bs, colors)
    save_image_geotif(classify_path, new_image_array, gt, proj, gdal.GDT_Byte)


if __name__ == "__main__":
    main()
