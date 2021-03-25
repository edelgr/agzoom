from osgeo import osr, gdal
from gdalconst import *
import os
import shutil
import cv2
from anotador import settings
from data_annotator.geoFunctions import jpg2geotif, GetGeoInfo

project_data_path = settings.MEDIA_ROOT


def put_geotiff_crs(src):
    # Opens source dataset
    src_ds = gdal.Open(src)
    format = "GTiff"
    driver = gdal.GetDriverByName(format)

    bn = os.path.splitext(src)[0]
    dst = bn + '_new.tif'
    # Open destination dataset
    dst_ds = driver.CreateCopy(dst, src_ds, 0)

    # Specify raster location through geotransform array
    # (uperleftx, scalex, skewx, uperlefty, skewy, scaley)
    # Scale = size of one pixel in units of raster projection
    # this example below assumes 100x100
    gt = [-80.2218, 0.000000632159, 0, 22.58, 0, -0.000000632159]

    # Set location
    dst_ds.SetGeoTransform(gt)

    # Get raster projection
    epsg = 4326
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    dest_wkt = srs.ExportToWkt()

    # Set projection
    dst_ds.SetProjection(dest_wkt)

    # Close files
    dst_ds = None
    src_ds = None
    return dst


def main():
    macro_project_id = '4-Clasificacion caña'
    project_id = '8-Clasificacion caña Sagua'
    image_date = '20200813'

    input_image = 'IMG_201215_151441_0070_RGB.JPG'
    input_path = project_data_path + 'album_patrones_drones/' + input_image
    output_path = jpg2geotif(input_path)
    new_tiff = put_geotiff_crs(output_path)

    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(new_tiff)

    bn = os.path.splitext(new_tiff)[0]
    prj = bn + '.prj'

    Projection.MorphToESRI()

    f = open(prj, 'w')
    f.write(Projection.ExportToWkt())
    f.close()

    (uperleftx, scalex, skewx, uperlefty, skewy, scaley) = GeoT
    tfw = bn + '.tfw'
    f = open(tfw, 'w')
    f.write(str(scalex))
    f.write('\n')
    f.write(str(skewx))
    f.write('\n')
    f.write(str(skewy))
    f.write('\n')
    f.write(str(scaley))
    f.write('\n')
    f.write(str(uperleftx))
    f.write('\n')
    f.write(str(uperlefty))
    f.write('\n')
    f.close()

if __name__ == "__main__":
    main()