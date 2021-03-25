import sys
from osgeo import ogr, osr, gdal
import os
import json
from data_annotator.masking import *
from data_annotator.cvmodel import build_cvred

sys.path.append('/home/edel/PycharmProjects/anotador')


def BoundingBox1(center, window_size=64):
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


def ganadora(lista):
    valor = np.amax(lista)
    if valor > 0.7:
        ind = np.where(lista == valor)
        return ind[0][0]
    else:
        return -1

def inside(x, y, ds_image, ds_shp):
    xoff, a, b, yoff, d, e = ds_image.GetGeoTransform()
    xp = a * x + b * y + a * 0.5 + b * 0.5 + xoff
    yp = d * x + e * y + d * 0.5 + e * 0.5 + yoff

    pt = ogr.Geometry(ogr.wkbPoint)
    pt.AddPoint(xp, yp)

    layer = ds_shp.GetLayer(0)
    layer.SetSpatialFilter(pt)

    for feature in layer:
        pepe = feature.items()
        return True
    return False



def clasif_shape_parcels(model, ds_image, ds_cloud_mask, ds_mask, ds_shp, outDataSource, colors, nclass):
    # Create the output shapefile
    outLayer = outDataSource.CreateLayer("cultivos", geom_type=ogr.wkbMultiPolygon)

    window_size = 7
    b_list = []
    proj = ds_image.GetProjection()
    target = osr.SpatialReference(wkt=proj)
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source, target)

    inLayer = ds_shp.GetLayer(0)

    # Add input Layer Fields to the output Layer
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # Add an clase field
    idField = ogr.FieldDefn("clase", ogr.OFTInteger)
    outLayer.CreateField(idField)

    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()

    # Add features to the ouput Layer
    for k in range(0, inLayer.GetFeatureCount()):
        # Get the input Feature
        inFeature = inLayer.GetFeature(k)
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)

        target_points = get_target_points_old(ds_mask, geom, ds_cloud_mask, window_size)
        if not target_points:
            outFeature.SetField("clase", "-1")
            continue

        vector = []
        for x in range(0, nclass+1):
            vector.append(0)

        for point in target_points:
            square = BoundingBox1(point, window_size)

            image_shape = [120, 120, ds_image.RasterCount]
            out_img = np.zeros(image_shape, dtype=float)
            from keras_preprocessing import image
            for i in range(1, ds_image.RasterCount + 1):
                band = ds_image.GetRasterBand(i)
                try:
                    data = band.ReadAsArray(square[0][0], square[0][1], window_size, window_size).astype('float')
                    x = cv2.resize(data, (120, 120)) / 255.
                    x = np.expand_dims(x, axis=2)
                    # x = image.ImageDataGenerator.standardize(x)
                    out_img[:, :, i - 1] = x[:, :, 0]
                except:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print("ERROR AT ", square[0][0], square[0][1], " COORDINATES")
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    xy = input("Continue?...")

            b_list.append(out_img)

            batch_x = np.array(b_list)

            predictions = model.predict(batch_x)
            # headers = {"content-type": "application/json"}
            # json_response = requests.post('http://localhost:8501/v1/models/cultivos_model/versions/1:predict', data=batch_x, headers=headers)
            # predictions = json.loads(json_response.text)['predictions']
            lab = ganadora(predictions[0])
            vector[lab] += 1

        max_value = max(vector)
        if max_value < 7:
            print("The class wins with ", max_value)

        lab = vector.index(max_value)

        if lab == len(vector)-1:
            lab = -1

        # print('lab :', str(lab), max_value)

        outFeature.SetField("clase", str(lab))

        b_list.clear()

        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
        outFeature = None

    # Save and close DataSources
    ds_shp = None
    outDataSource = None



def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))



def main():
    macro_project_id = '5'
    project_id = '9'
    image_date = '20201012'
    project_data_path = '/media/edel/Work/Projects_data/'
    input_image = 'spectral_features.tif'
    sentinel_path = project_data_path + 'images/' + project_id + '/sentinel/' + image_date + '/' + input_image
    input_mask = 'cloud_mask.tif'
    cloud_mask_path = project_data_path + 'images/' + project_id + '/sentinel/' + image_date + '/' + input_mask
    shape_mask_path = ""
    input_checkpoint = 'model-checkpoints/20201123-100220/CVRED_weights.1690-0.01.hdf5'
    checkpoint_path = project_data_path + 'macro_projects_data/' + macro_project_id + '/dataset_sentinel_unified/' + input_checkpoint
    input_class_indices = 'model-checkpoints/20201123-100220/CVRED_class_indices.json'
    class_indices_path = project_data_path + 'macro_projects_data/' + macro_project_id + '/dataset_sentinel_unified/' + input_class_indices
    input_shp = 'shape_macizo_norte/campos_costa_norte_vc.shp'
    shape_in_path = project_data_path + 'shape_features/' + project_id + '/' + input_shp
    output_shp = 'shape_macizo_norte/campos_costa_norte_vc_classified.shp'
    shape_out_path = project_data_path + 'shape_features/' + project_id + '/' + output_shp

    # gdf = geopandas.read_file(shape_in_path)
    # gdf.plot()
    # pyplot.show()

    with open(class_indices_path) as f:
        class_indices = json.load(f)

    nclass = len(class_indices)
    model = build_cvred(input_shape=(120, 120, 14), n_output_classes=nclass)
    model.load_weights(checkpoint_path)

    colors = []
    for ci in class_indices:
        c = ci['color']
        colors.append(hex_to_rgb(c))

    ds_shp = ogr.Open("projectedNew.shp", 1)
    ds_image = gdal.Open(sentinel_path)
    ds_cloud_mask = gdal.Open(cloud_mask_path)

    # Create the output Layer
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(shape_out_path):
        outDriver.DeleteDataSource(shape_out_path)

    outDataSource = outDriver.CreateDataSource(shape_out_path)
    ds_mask = "mask.tif"
    clasif_shape_parcels(model, ds_image, ds_cloud_mask, ds_mask, ds_shp, outDataSource, colors, nclass)


if __name__ == "__main__":
    main()
