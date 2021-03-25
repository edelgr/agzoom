from osgeo import ogr, osr, gdal
from anotador import settings
from data_annotator.geoFunctions import transform_points, BoundingCrop

project_data_path = settings.MEDIA_ROOT


def boundingBox(layer, image):
    """
    layer: capa previamente cargada del archivo shape
    image: imagen de referncia
    return: [x del punto superior izquierdo, y del punto, ancho del bounding box en pixeles, alto del bounding box]
    """
    envelopes = [feat.geometry().GetEnvelope() for feat in layer]
    coords = list(zip(*envelopes))
    minx, maxx = min(coords[0]), max(coords[1])
    miny, maxy = min(coords[2]), max(coords[3])
    points = transform_points(image, [(minx, maxy), (maxx, miny)])
    xOffset = abs(points[1][0] - points[0][0])
    yOffset = abs(points[1][1] - points[0][1])
    return [points[0][0], points[0][1], xOffset, yOffset]


def boundingBox2(image):
    """
    image: imagen de referncia
    return: [x del punto superior izquierdo, y del punto, ancho del bounding box en pixeles, alto del bounding box]
    """

    minx = -79.96
    miny = 22.88
    maxx = -80.55
    maxy = 22.32
    points = transform_points(image, [(minx, maxy), (maxx, miny)])
    xOffset = abs(points[1][0] - points[0][0])
    yOffset = abs(points[1][1] - points[0][1])
    return [points[0][0], points[0][1], xOffset, yOffset]


if __name__ == '__main__':
    project_id = '8'
    image_date = '20201012'
    input_shp = 'CP1_region.shp'
    shape_in_path = project_data_path + 'shape_features/' + project_id + '/' + input_shp
    output_shp = 'Cultivos_Varios_region_new.shp'
    shape_out_path = project_data_path + 'shape_features/' + project_id + '/' + output_shp
    input_image = 'spectral_features.tif'
    sentinel_in_path = project_data_path + 'images/' + project_id + '/sentinel/' + image_date + '/' + input_image
    output_image = 'area.tif'
    sentinel_out_path = project_data_path + 'images/' + project_id + '/sentinel/' + image_date + '/' + output_image

    # shp = ogr.Open(shape_in_path)
    img_ds = gdal.Open(sentinel_in_path)
    #
    #
    # shp = ogr.Open(shape_out_path)
    # layer = shp.GetLayer(0)
    # bound = boundingBox(layer, img_ds)

    bound = boundingBox2(img_ds)

    BoundingCrop(sentinel_in_path, bound[0], bound[1], bound[2], bound[3], sentinel_out_path)



