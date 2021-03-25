import os
import numpy as np
from shutil import copyfile

from anotador import settings
project_data_path = settings.MEDIA_ROOT

def create_dataset(macro_project_name, project_name, type_image, image_date):

    train_percent = 0.70
    validation_percent = 0.15

    directory = project_data_path + 'dataset/' + project_id + '/' + type_image + '/'
    print(directory)

    targetPath = project_data_path + 'macro_project_data/' + str(macro_project_id)
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath += '/' + project_id
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath += '/' + type_image
    try:
        os.mkdir(targetPath)
    except OSError:
        pass

    targetPath += '/' + image_date
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

    for subdir in sorted(os.listdir(directory + '/' + image_date)):
        if os.path.isdir(os.path.join(directory + image_date, subdir)):
            dir_classes = os.path.join(directory + image_date, subdir)
            try:
                os.mkdir(targetPath + '/' + "train_set" + '/' + subdir + '/')
            except OSError:
                pass

            try:
                os.mkdir(targetPath + '/' + "validation_set" + '/' + subdir + '/')
            except OSError:
                pass

            try:
                os.mkdir(targetPath + '/' + "test_set" + '/' + subdir + '/')
            except OSError:
                pass

            image_list = sorted(os.listdir(dir_classes))
            n = len(image_list)
            ltrain = int(n * train_percent)
            lvalidation = int(n * validation_percent)

            index_array = np.random.permutation(n)
            for i, index in enumerate(index_array):
                image = os.path.join(dir_classes, image_list[index])
                if i < ltrain:
                    outputPath = targetPath + '/' + "train_set" + '/' + subdir + '/' + image_list[index]
                elif i < (ltrain + lvalidation):
                    outputPath = targetPath + '/' + "validation_set" + '/' + subdir + '/' + image_list[index]
                else:
                    outputPath = targetPath + '/' + "test_set" + '/' + subdir + '/' + image_list[index]
                copyfile(image, outputPath)


if __name__ == "__main__":
    macro_project_id = '1'
    project_id_list = ['1']
    image_date_list = ['20201012']
    for project_id, image_date in zip(project_id_list, image_date_list):
        create_dataset(macro_project_id, project_id, 'sentinel', image_date)
