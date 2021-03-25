import sys
from osgeo import ogr, osr, gdal
import numpy as np
import cv2
import psycopg2
import pandas as pd
import os
import json
import geopandas
from matplotlib import pyplot
import struct
import requests
from data_annotator.cvmodel import build_cvred
from data_annotator.geoFunctions import BoundingBox1, transform_points

sys.path.append('/home/edel/PycharmProjects/anotador')


def ganadora(lista):
    valor = np.amax(lista)
    if valor > 0.7:
        ind = np.where(lista == valor)
        return ind[0][0]
    else:
        return -1

# Dado
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


def clasif_shape_parcels(model, ds_image, ds_mask, ds_shp, outDataSource, colors):
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
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount() - 1):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)

        center = geom.Centroid()
        center.Transform(transform)
        pto1 = center.GetPoints()
        # Convert geographic coordinates to pixel coordinates
        center = transform_points(ds_image, pto1, img2geo=False)
        print(center[0])

        px = center[0][0]
        py = center[0][1]

        # Extract pixel value
        band = ds_mask.GetRasterBand(1)
        try:
            structval = band.ReadRaster(px, py, 1, 1, buf_type=gdal.GDT_Byte)
        except OSError:
            print("Error leyendo el pto")

        result = struct.unpack('B', structval)[0]

        if result == band.GetNoDataValue() or result == 255:
            print('muestra sobre nube: ')
            outFeature.SetField("clase", str(-1))
            continue

        square = BoundingBox1(center[0], window_size)

        image_shape = [120, 120, ds_image.RasterCount]
        out_img = np.zeros(image_shape, dtype=float)
        from keras_preprocessing import image
        for i in range(1, ds_image.RasterCount + 1):
            band = ds_image.GetRasterBand(i)
            data = band.ReadAsArray(square[0][0], square[0][1], window_size, window_size).astype('float')
            x = cv2.resize(data, (120, 120)) / 255.
            x = np.expand_dims(x, axis=2)
            # x = image.ImageDataGenerator.standardize(x)
            out_img[:, :, i - 1] = x[:, :, 0]

        b_list.append(out_img)

        batch_x = np.array(b_list)

        # predictions = model.predict(batch_x)
        headers = {"content-type": "application/json"}
        json_response = requests.post('http://localhost:8501/v1/models/cultivos_model/versions/1:predict', data=batch_x, headers=headers)
        predictions = json.loads(json_response.text)['predictions']
        lab = ganadora(predictions[0])

        print('lab :', str(lab))

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
    mask_path = project_data_path + 'images/' + project_id + '/sentinel/' + image_date + '/' + input_mask
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

    ds_shp = ogr.Open(shape_in_path, 1)
    ds_image = gdal.Open(sentinel_path)
    ds_mask = gdal.Open(mask_path)

    # Create the output Layer
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(shape_out_path):
        outDriver.DeleteDataSource(shape_out_path)

    outDataSource = outDriver.CreateDataSource(shape_out_path)

    clasif_shape_parcels(model, ds_image, ds_mask, ds_shp, outDataSource, colors)


if __name__ == "__main__":
    main()
