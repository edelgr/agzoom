import os
import sys
from osgeo import gdal
import io
import data_annotator.ogr2ogr as map2shp

from osgeo import ogr

sys.path.append('/home/edel/PycharmProjects/anotador')

DATA_BASE_PATH = "/home/edel/Agricultura/CabaiguanEdel/Prueba1"


def main():
    # for a in os.listdir(DATA_BASE_PATH):
    #     fileName, fileExtension = os.path.splitext(a)
    #     cmd = 'ogr2ogr -f "ESRI Shapefile" %s %s' % (a, fileName + ".tab")
    #     os.system(cmd)

    for a in os.listdir(DATA_BASE_PATH):
        fileName, ext = os.path.splitext(a)
        if ext.lower() == '.tab':
            a = os.path.join(DATA_BASE_PATH, a)
            fileName = os.path.join(DATA_BASE_PATH, fileName)
            print('ogr2ogr -skipfailures -f "ESRI Shapefile" %s %s' % (a.replace(ext, '.shp'), fileName + ext))
            os.system('ogr2ogr -skipfailures -f "ESRI Shapefile" %s %s' % (a.replace(ext, '.shp'), fileName + ext))

    # map2shp.main(["ogr2ogr",  "-f", "ESRI Shapefile",  "/home/edel/Agricultura/CabaiguanEdel/Prueba1/NEIVA1.shp", "/home/edel/Agricultura/CabaiguanEdel/Prueba1/NEIVA1.tab"])

    # map2shp.main()
    # ogr2ogr.main([
    #     'ogr2ogr',
    #     '-f', 'GPKG', 'output.gpkg',
    #     'input.gpkg'
    # ])


if __name__ == "__main__":
    main()
