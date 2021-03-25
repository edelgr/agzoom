from osgeo import gdal, ogr
import numpy as np
import cv2
import random
import data_annotator.geoFunctions as geof

def create_mask(image, shape, output_name="mask"):
    in_ds = gdal.Open(image)
    in_band = in_ds.GetRasterBand(1)

    # Define pixel_size and NoData value of new raster
    pixel_size = in_ds.GetGeoTransform()[1]
    NoData_value = in_band.GetNoDataValue()

    # Filename of input OGR file
    vector_fn = shape

    # Filename of the raster Tiff that will be created
    raster_fn = output_name + '.tif'

    # Open the data source and read in the extent
    source_ds = ogr.Open(vector_fn)
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Byte)
    data = np.zeros((y_res, x_res), dtype='uint8')
    target_band = target_ds.GetRasterBand(1)
    target_band.WriteArray(data)
    target_ds.SetProjection(in_ds.GetProjection())
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    band = target_ds.GetRasterBand(1)

    if NoData_value is not None:
        band.SetNoDataValue(NoData_value)

    # Rasterize
    gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[255])


def get_target_points_old(mask_raster, geometry, cloud_mask_raster, window_size):
    """
    This function extracts the points to be classified inside a geometry
    :param mask_raster: Path to the mask raster
    :param geometry: geometry to extract the points
    :return: a list of points randomly extracted
    """
    # Reading mask rasters
    mask_ds = gdal.Open(mask_raster)
    mask_array = mask_ds.GetRasterBand(1).ReadAsArray()
    cloud_mask = cloud_mask_raster.GetRasterBand(1)

    # Applying erosion to the mask for 7 pixels
    kernel = np.ones((3, 3), dtype='uint8')
    it = (window_size//2)+1
    for i in range(it):
        mask_array = cv2.erode(mask_array, kernel)

    # Randomizing and listing the points to extract
    points_list = []
    x_min, x_max, y_min, y_max = geometry.GetEnvelope()
    top_left, bottom_right = geof.transform_points(mask_ds, [(x_min, y_min), (x_max, y_max)])
    cont = 1
    iterations = 500
    x_min, y_min = top_left
    x_max, y_max = bottom_right
    # x_min, x_max, y_min, y_max = int(x_min), int(x_max), int(y_min), int(y_max)
    if y_min > y_max:
        ymax = y_max+0
        y_max = y_min+0
        y_min = ymax
        del ymax

    while cont < 8 and iterations > 0:
        iterations -= 1
        x = random.randint(x_min, x_max)
        y = random.randint(y_min, y_max)
        # cloud_point = geof.transform_points(mask_ds, [(x, y)], True)
        # cloud_point = geof.transform_points(cloud_mask_raster, cloud_point)
        # cloud_val = cloud_mask.ReadAsArray(cloud_point[0], cloud_point[1], 1, 1)
        cloud_val = cloud_mask.ReadAsArray(x, y, 1, 1)

        if mask_array[y, x] == 255 and cloud_val[0, 0] == 0:
            points_list.append((x, y))
            cont += 1

    if len(points_list) < 7:
        print("The list has "+str(len(points_list)))

    return points_list


def get_target_points(mask_raster, cloud_mask, geometry, window_size):
    # Reading mask raster
    mask_ds = gdal.Open(mask_raster)
    mask_array = mask_ds.GetRasterBand(1).ReadAsArray()

    # Applying erosion to the mask for window_size X window_size pixels
    it = (window_size//2)+1
    for i in range(it):
        kernel = np.ones((3, 3), dtype='uint8')
        mask_array = cv2.erode(mask_array, kernel)

    # Randomizing and listing the points to extract
    points_list = []
    x_min, x_max, y_min, y_max = geometry.GetEnvelope()
    top_left, bottom_right = geof.transform_points(mask_ds, [(x_min, y_min), (x_max, y_max)])
    cont = 1
    iterations = 100
    x_min, y_min = top_left
    x_max, y_max = bottom_right
    # x_min, x_max, y_min, y_max = int(x_min), int(x_max), int(y_min), int(y_max)
    if y_min > y_max:
        ymax = y_max + 0
        y_max = y_min + 0
        y_min = ymax
        del ymax

    mask_array = mask_array[y_min:y_max, x_min:x_max]


    while cont < 8 and iterations > 0:
        iterations -= 1
        x = random.randint(x_min, x_max)
        y = random.randint(y_min, y_max)
        if mask_array[y, x] == 255 and cloud_mask==0:
            points_list.append((x, y))
            cont += 1

    if len(points_list) < 7:
        print("The list has " + str(len(points_list)))
    else:
        print("OK")

    return points_list

def testing_get_target_points_old():
    mask_raster = "new_mask.tif"
    shape = ogr.Open(r"C:\Users\Migue\PycharmProjects\Mangle\projectedNew.shp")
    layer = shape.GetLayer()
    feature = layer[1]
    geom = feature.GetGeometryRef()
    lista = get_target_points_old(mask_raster, geom)
    print(lista)


if __name__ == '__main__':
    project_id = '9'
    project_data_path = '/media/edel/Work/Projects_data/'
    input_shp = 'shape_macizo_norte/campos_costa_norte_vc.shp'
    shape_in_path = project_data_path + 'shape_features/' + project_id + '/' + input_shp
    image_date = '20201012'
    input_image = 'spectral_features.tif'
    sentinel_path = project_data_path + 'images/' + project_id + '/sentinel/' + image_date + '/' + input_image
    ds = gdal.Open(sentinel_path)
    shape = ogr.Open(shape_in_path)
    geof.reproject(shape, ds.GetProjection(), False)
    create_mask(sentinel_path, "projectedNew.shp")