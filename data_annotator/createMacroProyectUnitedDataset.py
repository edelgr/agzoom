import os
import numpy as np
import datetime
from shutil import copyfile
from anotador import settings
project_data_path = settings.MEDIA_ROOT

def create_dataset_unify(macro_project_name, creation_date, project_name, type_image, image_date):
    targetPath = project_data_path + 'macro_projects_data/' + macro_project_name
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath = project_data_path + 'macro_projects_data/' + macro_project_name + '/' + creation_date + '/dataset_unificado/'

    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    try:
        os.mkdir(targetPath + '/' + "train_set")
    except OSError:
        pass

    try:
        os.mkdir(targetPath + '/' + "validation_set")
    except OSError:
        pass

    try:
        os.mkdir(targetPath + '/' + "test_set")
    except OSError:
        pass

    directory = project_data_path + 'macro_projects_data/' + macro_project_name + '/' + project_name + '/' + type_image + '/' + image_date

    for subdir in sorted(os.listdir(directory + '/' + "train_set")):
        if os.path.isdir(os.path.join(directory + '/' + "train_set", subdir)):
            dir_classes = os.path.join(directory + '/' + "train_set", subdir)
            try:
                os.mkdir(targetPath + '/' + "train_set" + '/' + subdir + '/')
            except OSError:
                pass

            image_list = sorted(os.listdir(dir_classes))
            for img in image_list:
                image = os.path.join(dir_classes, img)
                outputPath = targetPath + '/' + "train_set" + '/' + subdir + '/' + img
                copyfile(image, outputPath)

    for subdir in sorted(os.listdir(directory + '/' + "validation_set")):
        if os.path.isdir(os.path.join(directory + '/' + "validation_set", subdir)):
            dir_classes = os.path.join(directory + '/' + "validation_set", subdir)
            try:
                os.mkdir(targetPath + '/' + "validation_set" + '/' + subdir + '/')
            except OSError:
                pass

            image_list = sorted(os.listdir(dir_classes))
            for img in image_list:
                image = os.path.join(dir_classes, img)
                outputPath = targetPath + '/' + "validation_set" + '/' + subdir + '/' + img
                copyfile(image, outputPath)

    for subdir in sorted(os.listdir(directory + '/' + "test_set")):
        if os.path.isdir(os.path.join(directory + '/' + "test_set", subdir)):
            dir_classes = os.path.join(directory + '/' + "test_set", subdir)

            try:
                os.mkdir(targetPath + '/' + "test_set" + '/' + subdir + '/')
            except OSError:
                pass

            image_list = sorted(os.listdir(dir_classes))
            for img in image_list:
                image = os.path.join(dir_classes, img)
                outputPath = targetPath + '/' + "test_set" + '/' + subdir + '/' + img
                copyfile(image, outputPath)


if __name__ == "__main__":
    macro_project_name = '1-clasificacion de cultivos varios'
    project_name_list = ['1-Cultuvos Varios Cabaiguan - Neiva',
                       '1-Cultuvos Varios Cabaiguan - Neiva',
                       '1-Cultuvos Varios Cabaiguan - Neiva',
                       '1-Cultuvos Varios Cabaiguan - Neiva']
    image_date_list = ['20200626', '20200629', '20200711', '20200716']
    creation_date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for project_name, image_date in zip(project_name_list, image_date_list):
        create_dataset_unify(macro_project_name, creation_date, project_name, 'sentinel', image_date)
