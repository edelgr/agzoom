from osgeo import ogr, osr, gdal
import os
import glob
import cv2
import numpy as np
from os import listdir
from os.path import isfile
import gdal2tiles
from gdalconst import *
import affine
from anotador import settings

project_data_path = settings.MEDIA_ROOT


def create_raster_from_jp2(bands, name, DataType):
    """
    :param bands: A list with the names of every input channel
    :param name: A string with the name of the output file
    :return: A single raster which contains all the input bands
    """
    firstBandName = bands[0]
    firstBand = gdal.Open(firstBandName)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(name, firstBand.RasterXSize, firstBand.RasterYSize, len(bands), DataType)
    out_ds.SetProjection(firstBand.GetProjection())
    out_ds.SetGeoTransform(firstBand.GetGeoTransform())
    del firstBand

    contrats = -0.35
    brightness = 10.0
    for i in range(1, len(bands) + 1):
        bandName = bands[i - 1]
        ds = gdal.Open(bandName)
        band = ds.GetRasterBand(1)
        data = band.ReadAsArray()

        norm_img1 = cv2.normalize(data, None, alpha=contrats, beta=brightness,
                                  norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        norm_img1 = np.clip(norm_img1, 0, 1)
        norm_img1 = (255 * norm_img1).astype(np.uint8)

        out_band = out_ds.GetRasterBand(i)
        out_band.WriteArray(norm_img1)
        del data

    out_ds.FlushCache()
    for i in range(1, len(bands) + 1):
        out_ds.GetRasterBand(i).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds


def sentinel_background_image(processing_dir_path, image_path):
    if image_path[4:10] == 'MSIL2A':
        path = processing_dir_path + image_path + '/R10m'
    else:
        path = processing_dir_path + image_path

    files = [f for f in listdir(path) if isfile(path + '/' + f)]

    red = None
    green = None
    blue = None
    for i in range(len(files)):
        if image_path[4:10] == 'MSIL2A':
            name = files[i][-10:-8]
        else:
            name = files[i][-6:-4]

        if name == '02':
            blue = path + "/" + files[i]
        if name == '03':
            green = path + "/" + files[i]
        if name == '04':
            red = path + "/" + files[i]

    files_bands = [red, green, blue]
    output_file = processing_dir_path + "/" + "background_image.tif"
    create_raster_from_jp2(files_bands, output_file, gdal.GDT_Byte)


def drones_background_image(infile, injgw, outfile):
    ds_in = gdal.Open(infile)
    band1_in = ds_in.GetRasterBand(1)
    band2_in = ds_in.GetRasterBand(2)
    band3_in = ds_in.GetRasterBand(3)
    nRows = ds_in.RasterYSize
    nCols = ds_in.RasterXSize

    gtiff_driver = gdal.GetDriverByName('GTiff')

    # Set up the dataset
    ds_out = gtiff_driver.Create(outfile, nCols, nRows, 3, gdal.GDT_Byte)

    if injgw is not None:
        with open(injgw, 'r') as fp:
            a = affine.loadsw(fp.read())
            gt = a.to_gdal()
    else:
        gt = ds_in.GetGeoTransform()

    ds_out.SetGeoTransform(gt)

    prj = osr.SpatialReference()
    prj.ImportFromEPSG(4326)
    ds_out.SetProjection(prj.ExportToWkt())

    band1_out = ds_out.GetRasterBand(1)
    band2_out = ds_out.GetRasterBand(2)
    band3_out = ds_out.GetRasterBand(3)

    for ThisRow in range(nRows):
        ThisLineBand1 = band1_in.ReadAsArray(0, ThisRow, nCols, 1)
        ThisLineBand2 = band2_in.ReadAsArray(0, ThisRow, nCols, 1)
        ThisLineBand3 = band3_in.ReadAsArray(0, ThisRow, nCols, 1)


        if ThisRow % 100 == 0:
            print("Scanning %d  of %d" % (ThisRow, nRows))

        band1_out.WriteArray(ThisLineBand1, 0, ThisRow)
        band2_out.WriteArray(ThisLineBand2, 0, ThisRow)
        band3_out.WriteArray(ThisLineBand3, 0, ThisRow)

    ds_out.FlushCache()
    for i in range(1, 4):
        ds_out.GetRasterBand(i).ComputeStatistics(False)
    ds_out.BuildOverviews('average', [2, 4, 8, 16, 32])

    del ds_in
    del ds_out


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
        tarjet_shape[2] = ds.RasterCount - 1
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


def reproject(shape, targetprj, spatial_ref=True):
    """
    Extracting layers from shapefiles with their sourceprj
    and project each feature from source layer with the targeproj
    shape : shape of input
    targetprj : projection target
    """
    layer1 = shape.GetLayer()

    # get spatial reference and transformation
    sourceprj = layer1.GetSpatialRef()

    if not spatial_ref:
        src = osr.SpatialReference()
        src.ImportFromWkt(targetprj)
        targetprj = src

    transform = osr.CoordinateTransformation(sourceprj, targetprj)

    to_fill = ogr.GetDriverByName("Esri Shapefile")
    ds = to_fill.CreateDataSource("projectedNew.shp")
    outlayer = ds.CreateLayer('', targetprj, ogr.wkbPolygon)
    outlayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))

    # apply transformation
    i = 0

    for feature in layer1:
        transformed = feature.GetGeometryRef()
        transformed.Transform(transform)

        geom = ogr.CreateGeometryFromWkb(transformed.ExportToWkb())
        defn = outlayer.GetLayerDefn()
        feat = ogr.Feature(defn)
        feat.SetField('id', i)
        feat.SetGeometry(geom)
        outlayer.CreateFeature(feat)
        i += 1
        feat = None

    ds = None


def transform_points(image, points, img2geo=False):
    """
    Recibe una imagen abierta con GDAL y una lista de puntos en coordenadas geograficas y devuelve una lista de
    puntos en coordenadas de la imagen de referencia.
    :param image: Image Data Set from GDAL
    :param points: list
    :param img2geo: Si es True, la transformacion es de coordenadas de imagen a coordenadas geograficas.
                    Si es False es lo contrario.
    :return: list
    """
    gt = image.GetGeoTransform()

    if not img2geo:
        gt = gdal.InvGeoTransform(gt)
    transformed_points = []

    for coord in points:
        offsets = gdal.ApplyGeoTransform(gt, coord[0], coord[1])
        xoff, yoff = map(int, offsets)
        transformed_points.append([xoff, yoff])

    return transformed_points


def intersection(shape1, shape2, path=""):
    """
    Creates a Shapefile with the intersection areas between the shapefile1 and the shapefile2.
    :param shape1: Shapefile which represents the main area, which will contain the geometrys from the shapefile2
    :param shape2: Shapefile which contains the smaller geometries
    :param path: The relative path where the resulting shapefile will be saved
    """
    driver = ogr.GetDriverByName("Esri Shapefile")
    lyr1 = shape1.GetLayer(0)

    for feat1 in lyr1:
        first = True
        geom1 = feat1.geometry().Clone()
        lyr2 = shape2.GetLayer(0)
        out_name = feat1.GetField(0)
        for feat2 in lyr2:
            print(True)
            geom2 = feat2.geometry().Clone()
            if geom2.Intersects(geom1):
                if first:
                    if path == "":
                        dstshp = driver.CreateDataSource(out_name + '.shp')
                    else:
                        dstshp = driver.CreateDataSource(path + "//" + out_name + '.shp')
                    dstlayer = dstshp.CreateLayer(out_name, lyr2.GetSpatialRef(), geom_type=ogr.wkbPolygon)
                    dstlayer.CreateFields(lyr2.schema)
                    first = False

                intersection = geom2.Intersection(geom1)
                dstfeature = ogr.Feature(dstlayer.GetLayerDefn())
                dstfeature.SetGeometry(intersection)
                for i in range(feat2.GetFieldCount()):
                    value = feat2.GetField(i)
                    dstfeature.SetField(i, value)
                    dstlayer.CreateFeature(dstfeature)
                dstfeature.Destroy()


def get_geom_center(geom):
    """
    :param geom: A geometry object or a points list
    :return: The coordinates of the geometry's center (tuple)
    """
    if str(type(geom)) == "<class 'list'>":
        points = geom
    else:
        ring = geom.GetGeometryRef(0)
        points = ring.GetPoints()

    xList = []
    yList = []
    for i in points:
        xList.append(i[0])
        yList.append(i[1])
    xList.sort()
    yList.sort()
    """
    print(xList)
    print(yList)
    print("xList", xList[0], xList[len(xList)-1])
    print("yList", yList[0], yList[len(yList)-1])
    """
    xMed = (xList[0] + xList[len(xList) - 1]) / 2.0
    yMed = (yList[0] + yList[len(yList) - 1]) / 2.0
    center = (int(round(xMed)), int(round(yMed)))
    """x, y = zip(*points)
    plt.plot(x, y, 'k',xMed,yMed,'bs')
    plt.show()
    """
    return center


# def create_square(center, window_size=64):
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


# def world_to_pixel(gt, x, y):
#     ulx = gt[0]
#     uly = gt[3]
#     xdist = gt[1]
#     ydist = gt[5]
#     pixel = int((x - ulx) / xdist)
#     line = -int((uly - y) / ydist)
#     return pixel, line


def BoundingBox2(layer, image):
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


def BoundingBox3(envelopes, image):
    """
    envelopes: lista de los puntos del rectangulo
    image: imagen de referncia
    return: [x del punto superior izquierdo, y del punto, ancho del bounding box en pixeles, alto del bounding box]
    """
    coords = envelopes
    minx = coords[5]
    maxx = coords[1]
    miny = coords[0]
    maxy = coords[4]
    points = transform_points(image, [(minx, maxy), (maxx, miny)])
    xOffset = abs(points[1][0] - points[0][0])
    yOffset = abs(points[1][1] - points[0][1])
    return [points[0][0], points[0][1], xOffset, yOffset]


def CreateNumberMap(img, layer, xSize, ySize):
    numbMap = np.zeros((ySize, xSize), dtype='uint16')
    for feat in layer:
        num = int(feat.GetField(0))
        ring = feat.geometry().GetGeometryRef(0)
        points = ring.GetPoints()
        """
        if num == 22:
            geom22 = points[:]
        if num == 44:
            x, y = zip(*points)
            x1, y1 = zip(*geom22)
            plt.plot(x, y, 'k', x1, y1, 'k')
            plt.show()
        """

        try:
            mask = np.zeros((ySize, xSize), dtype='uint8')
            noMask = np.ones((ySize, xSize), dtype='uint8')
            points = transform_points(img, points, imgToGeo=False)
            points = np.array(points, np.int32)
            points = points.reshape((-1, 1, 2))
            cv2.fillConvexPoly(mask, points, 1)
            cv2.fillConvexPoly(noMask, points, 0)
            noMask = noMask.astype('uint16')
            mask = mask.astype('uint16')
            numbMap = np.multiply(numbMap, noMask)
            val = num + 100
            numbMap = np.add(numbMap, mask * val)
            print(num)
            # print("Parcela", num, "Maximo Mask", maximo, "Maximo Map", maximo1)

        except:
            print("Something was wrong")
    print(np.amax(numbMap))
    band = img.GetRasterBand(1)
    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create('MapaParcelasCropped.tif', band.XSize, band.YSize, 1, band.DataType)

    out_ds.SetProjection(img.GetProjection())
    out_ds.SetGeoTransform(img.GetGeoTransform())

    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(numbMap)
    out_ds.FlushCache()
    out_ds.GetRasterBand(1).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    del out_ds
    return numbMap


def BoundingCrop(img, xo, yo, newX, newY, outName):
    """
    img: Imagen original en GeoTiff a recortar
    xo, yo : coordenadas del vertice superior izquierdo en coordenadas de imagen
    newX, newY: nuevo ancho y alto de imagen en cantidad de pixeles
    outName: Nombre de la imagen GeoTiff de salida
    """
    in_ds = gdal.Open(img)
    bands = in_ds.RasterCount

    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(outName, newX, newY, 1, in_ds.GetRasterBand(1).DataType)

    out_gt = list(in_ds.GetGeoTransform())
    offsets = gdal.ApplyGeoTransform(in_ds.GetGeoTransform(), xo, yo)
    out_gt[0] = offsets[0]
    out_gt[3] = offsets[1]

    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.SetGeoTransform(out_gt)

    for i in range(1, bands + 1):
        in_band = in_ds.GetRasterBand(i)
        data = in_band.ReadAsArray(xo, yo, newX, newY)
        out_band = out_ds.GetRasterBand(i)
        out_band.WriteArray(data)
        out_ds.FlushCache()

    for i in range(1, bands + 1):
        out_ds.GetRasterBand(1).ComputeStatistics(False)
        out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])

    del out_ds


def CropImageByGeom(input_img, target_img, shape, root=''):
    """
    input_img: Imagen geotiff de entrada
    target_img: Imagen geotiff con anotaciones de clases
    shape: Geometria de las parcelas
    root: camino relativo a la carpeta
    Esta funcion toma el punto central de la geometria de cada parcela y a partir de este crea un patch de 64x64 y guarda
    los resultados en dos directorios, las muestras de entrada y las muestras objetivo.
    """
    gtiff_driver = gdal.GetDriverByName('GTiff')

    ds1 = gdal.Open(input_img)
    ds2 = gdal.Open(target_img)

    bandsCount = ds1.RasterCount
    shp = ogr.Open(shape)
    layer = shp.GetLayer(0)

    inputPath = root + "//input_Dir"
    try:
        os.mkdir(inputPath)
    except OSError:
        print("Creation of the directory %s failed" % inputPath)
    else:
        print("Successfully created the directory %s " % inputPath)

    targetPath = root + "//target_Dir"
    try:
        os.mkdir(targetPath)
    except OSError:
        print("Creation of the directory %s failed" % targetPath)
    else:
        print("Successfully created the directory %s " % targetPath)
    noDeleted = []

    for feat in layer:
        try:
            ring = feat.geometry().GetGeometryRef(0)
            points = ring.GetPoints()
            center = get_geom_center(points)
            center = transform_points(ds1, [center])
            square = BoundingBox1(center[0])

            num = int(feat.GetField(0))
            if num < 10:
                name = "000" + str(num)
            elif num < 100:
                name = "00" + str(num)
            elif num < 1000:
                name = "0" + str(num)
            else:
                name = str(num)

            out_ds = gtiff_driver.Create(inputPath + "//" + name + ".tif", 64, 64, ds1.RasterCount,
                                         ds1.GetRasterBand(1).DataType)
            for i in range(1, ds1.RasterCount + 1):
                band = ds1.GetRasterBand(i)
                data = band.ReadAsArray(square[0][0], square[0][1], 64, 64)
                out_band = out_ds.GetRasterBand(i)
                out_band.WriteArray(data)
                del data
            out_ds.FlushCache()
            for i in range(1, ds1.RasterCount + 1):
                out_ds.GetRasterBand(i).ComputeStatistics(False)
            out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])

            del out_ds

            # ojo con la proyeccion
            targetData = ds2.GetRasterBand(1).ReadAsArray(square[0][0], square[0][1], 64, 64)
            cv2.imwrite(targetPath + "//" + name + ".png", targetData)

        except:
            try:
                del out_ds
                os.remove(inputPath + "//" + name + ".tif")
                os.remove(targetPath + "//" + name + ".npy")
            except:
                print(name, "no deleted")
                noDeleted.append(name)
            print("Something was wrong")
    for name in noDeleted:
        try:
            os.remove(inputPath + "//" + name + ".tif")
            os.remove(targetPath + "//" + name + ".npy")
            print(name, "successfully deleted")
        except:
            print(name, "no deleted")


def GetGeoInfo(FileName):
    SourceDS = gdal.Open(FileName, GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataType = gdal.GetDataTypeName(DataType)
    return NDV, xsize, ysize, GeoT, Projection, DataType


# Function to write a new file.
def CreateGeoTiff(Name, Array, driver, NDV, xsize, ysize, GeoT, Projection, DataType):
    '''
    crea un fichero geotiff a partir de un arreglo numpy
    '''
    if DataType == 'Float32':
        DataType = gdal.GDT_Float32
    NewFileName = Name + '.tif'
    # Set nans to the original No Data Value
    if NDV is not None:
        Array[np.isnan(Array)] = NDV
    else:
        NDV = 0
    # Set up the dataset
    DataSet = driver.Create(NewFileName, xsize, ysize, 1, DataType)
    # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection.ExportToWkt())
    # Write the array
    DataSet.GetRasterBand(1).WriteArray(Array)
    DataSet.GetRasterBand(1).SetNoDataValue(NDV)
    return NewFileName


def create_patches(img, shape):
    gtiff_driver = gdal.GetDriverByName('GTiff')
    ds = gdal.Open(img)
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()

    shape = ogr.Open(shape)
    layer = shape.GetLayer(0)

    for feat in layer:
        ring = feat.geometry().GetGeometryRef(0)
        points = ring.GetPoints()
        center = get_geom_center(points)
        center = transform_points(ds, center)
        square = BoundingBox1(center)
        leftCorner = square[0]
        rightCorner = square[2]


def jpg2geotif(bandName):
    bn = os.path.splitext(bandName)[0]
    ds = gdal.Open(bandName)
    band1 = ds.GetRasterBand(1)
    band2 = ds.GetRasterBand(2)
    band3 = ds.GetRasterBand(3)
    xsize = band1.XSize
    ysize = band1.YSize
    data1 = band1.ReadAsArray()
    data2 = band2.ReadAsArray()
    data3 = band3.ReadAsArray()

    new_filename = bn + '.tif'
    gtiff_driver = gdal.GetDriverByName('GTiff')

    # Set up the dataset
    DataSet = gtiff_driver.Create(new_filename, xsize, ysize, 3, gdal.GDT_UInt16)
    DataSet.SetProjection(ds.GetProjection())
    DataSet.SetGeoTransform(ds.GetGeoTransform())
    # Write the array
    DataSet.GetRasterBand(1).WriteArray(data1)
    DataSet.GetRasterBand(2).WriteArray(data2)
    DataSet.GetRasterBand(3).WriteArray(data3)
    DataSet.FlushCache()
    band1 = None
    band2 = None
    band3 = None
    DataSet = None
    ds = None

    # for i in range(1, 4):
    #     DataSet.GetRasterBand(i).ComputeStatistics(False)
    #
    # DataSet.BuildOverviews("average", [2, 4, 8, 16, 32])
    #
    # del DataSet
    return new_filename


def tif2geotif(bandName):
    bn = os.path.splitext(bandName)[0]
    ds = gdal.Open(bandName)

    band1 = ds.GetRasterBand(1)
    band2 = ds.GetRasterBand(2)
    band3 = ds.GetRasterBand(3)
    xsize = band1.XSize
    ysize = band1.YSize
    print('XSize: ', xsize)
    print('YSize: ', ysize)
    print("Leyendo banda 1")
    data1 = band1.ReadAsArray()
    print("Leyendo banda 2")
    data2 = band2.ReadAsArray()
    print("Leyendo banda 3")
    data3 = band3.ReadAsArray()

    new_filename = bn + '_new.tif'
    gtiff_driver = gdal.GetDriverByName('GTiff')

    # Set up the dataset
    DataSet = gtiff_driver.Create(new_filename, xsize, ysize, 3, gdal.GDT_Byte)
    DataSet.SetGeoTransform(ds.GetGeoTransform())
    DataSet.SetProjection(ds.GetProjection())

    # Write the array
    print("Escribiendo banda 1")
    DataSet.GetRasterBand(1).WriteArray(data1)
    print("Escribiendo banda 2")
    DataSet.GetRasterBand(2).WriteArray(data2)
    print("Escribiendo banda 3")
    DataSet.GetRasterBand(3).WriteArray(data3)
    DataSet.FlushCache()
    band1 = None
    band2 = None
    band3 = None
    DataSet = None
    ds = None

    # for i in range(1, 4):
    #     DataSet.GetRasterBand(i).ComputeStatistics(False)
    #
    # DataSet.BuildOverviews("average", [2, 4, 8, 16, 32])
    #
    del ds
    del DataSet
    return new_filename


def convert_tms(pasta):
    contentz = os.listdir(pasta)
    print(contentz)
    for z in contentz:
        if os.path.isdir(pasta + z):
            print('Z: ' + z)
            nz = float(z)
            os.chdir(pasta + z)
            contentx = os.listdir(pasta + z)

            for x in contentx:
                if os.path.isdir(pasta + "/" + z + "/" + x):
                    print('X: ' + x)
                    os.chdir(pasta + "/" + z + "/" + x)

                    for png in sorted(glob.glob('*.png')):
                        ny = float(png.split('.')[0])
                        ny_new = int((2 ** nz) - ny - 1)
                        os.rename(png, str(ny_new) + ".png")

                        print('Y: ' + png.split('.')[0] + ' | ' + str(ny_new))

                print('\n')

        print('\n')

    print('Tiles successfully converted ...!')


def tiler(input_file, output_dir):
    options = {'zoom': (12, 22), 'tilesize': 256, 'w': '', 'nb_processes': 24, 'resume': True}

    gdal2tiles.generate_tiles(input_file, output_dir, **options)


def repare(input_folder):
    folder = sorted(os.listdir(input_folder))
    for i, file in enumerate(folder):
        print(i)
        subfolder = os.path.join(input_folder, file)
        files = sorted(os.listdir(subfolder))
        for f in files:
            f = os.path.join(subfolder, f)
            print(f)
            sz = os.stat(f)
            if sz.st_size == 0:
                print('BBBBBBBBBBBBBBBBBBBBBBBBORRAR :', f)
                os.remove(f)
