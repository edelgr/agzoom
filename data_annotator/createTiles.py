from osgeo import gdal
import os
import glob
from anotador import settings
import gdal2tiles

project_data_path = settings.MEDIA_ROOT


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


def tiler(type, inputFile, outputDir):
    ds1 = gdal.Open(inputFile)
    s_srs = ds1.GetProjection()
    del ds1

    if type == 'sentinel':
        options = {'zoom': (10, 15), 'tilesize': 256, 's_srs': s_srs, 'nb_processes': 4, 'webviewer': 'openlayers',
                   'resume': True}
    else:
        options = {'zoom': (15, 22), 'tilesize': 256, 's_srs': s_srs, 'nb_processes': 4, 'webviewer': 'openlayers',
                   'resume': True}

    gdal2tiles.generate_tiles(inputFile, outputDir, **options)


if __name__ == '__main__':
    imageType = 'sentinel'
    input_image = 'ripe.tif'
    ouput_folder = 'ripe_mbtiles'
    pn1 = 'Cultuvos Varios Cabaiguan - Neiva'
    project_id_list = ['1', '1', '1', '1', '1', '1']
    image_date_list = ['20200527', '20200626', '20200711', '20200716', '20210102']

    i = 0
    for project_id, date in zip(project_id_list, image_date_list):
        i = i + 1
        print(i)
        project_name = str(project_id) + '-' + pn1
        path = project_data_path + 'images/' + project_name + '/' + imageType + '/' + date + "/"
        input_file = path + input_image
        output_dir = path + '/' + ouput_folder

        try:
            os.mkdir(output_dir)
        except OSError:
            pass
        tiler(imageType, input_file, output_dir)
