import datetime
import psycopg2
import pandas as pd
from anotador import settings

import tensorflow as tf
import os
import sys
from packaging import version
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
import io
import itertools
import json

sys.path.append('/home/edel/PycharmProjects/anotador')

from data_annotator.cvmodel2 import build_cvred
from data_annotator.msi_image_generator import MsiImageDataGenerator

project_data_path = settings.MEDIA_ROOT

def plot_confusion_matrix(cm, class_names):
    """
  Returns a matplotlib figure containing the plotted confusion matrix.

  Args:
    cm (array, shape = [n, n]): a confusion matrix of integer classes
    class_names (array, shape = [n]): String names of the integer classes
  """
    figure = plt.figure(figsize=(8, 8))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("Confusion matrix")
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)

    # Normalize the confusion matrix.
    cm = np.around(cm.astype('float') / cm.sum(axis=1)[:, np.newaxis], decimals=2)

    # Use white text if squares are dark; otherwise black.
    threshold = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        color = "white" if cm[i, j] > threshold else "black"
        plt.text(j, i, cm[i, j], horizontalalignment="center", color=color)

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    return figure


def plot_to_image(figure):
    """Converts the matplotlib plot specified by 'figure' to a PNG image and
    returns it. The supplied figure is closed and inaccessible after this call."""
    # Save the plot to a PNG in memory.
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    # Closing the figure prevents it from being displayed directly inside
    # the notebook.
    plt.close(figure)
    buf.seek(0)
    # Convert PNG buffer to TF image
    image = tf.image.decode_png(buf.getvalue(), channels=4)
    # Add the batch dimension
    image = tf.expand_dims(image, 0)
    return image


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def train_cvred(macro_project_id, model, target_size, batch_size, dataset_path, training_path_prefix,
                testing_path_prefix, history_file_path, history_filename, checkpoint_path, checkpoint_prefix,
                number_of_epochs, tensorboard_log_path):

    train_images_dir = dataset_path + training_path_prefix
    test_images_dir = dataset_path + testing_path_prefix

    train_datagen = MsiImageDataGenerator(rescale=1. / 255)
    # brightness_range=[0.0, 0.2],
    # rotation_range=90,
    # width_shift_range=0.1,
    # height_shift_range=0.1,
    # horizontal_flip=True)

    test_datagen = MsiImageDataGenerator(rescale=1. / 255)

    training_set_generator = train_datagen.flow_from_directory(train_images_dir,
                                                               target_size,
                                                               channels=14,
                                                               batch_size=batch_size,
                                                               class_mode='categorical',
                                                               shuffle=True,
                                                               seed=42)

    test_set_generator = test_datagen.flow_from_directory(test_images_dir,
                                                          target_size,
                                                          channels=14,
                                                          batch_size=batch_size,
                                                          class_mode='categorical',
                                                          shuffle=True,
                                                          seed=42)

    step_size_train = training_set_generator.n // training_set_generator.batch_size
    step_size_validation = test_set_generator.n // test_set_generator.batch_size

    class_index = training_set_generator.class_indices
    class_index_path = checkpoint_path + '/%s_class_indices.json' % checkpoint_prefix

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

    sql = 'select color, label_name from data_annotator_label as l where l.macro_project_id=' + str(macro_project_id)

    df_label = pd.read_sql(sql, connection)

    legend = []

    for i, cla in enumerate(df_label['label_name']):
        json_dict = {'label': df_label['label_name'][i], 'color': df_label['color'][i]}
        legend.append(json_dict)

    with open(class_index_path, 'w') as json_file:
        json.dump(legend, json_file)

    check_pointer = tf.keras.callbacks.ModelCheckpoint(
        checkpoint_path + '/%s_weights.{epoch:02d}-{val_loss:.2f}.hdf5' % checkpoint_prefix,
        monitor='val_loss', mode='auto', save_best_only=True)

    csv_logger = tf.keras.callbacks.CSVLogger(filename=history_file_path + "/" + history_filename)

    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=tensorboard_log_path, histogram_freq=1)

    # file_writer_cm = tf.summary.create_file_writer(tensorboard_log_path + '/cm')

    # def log_confusion_matrix(epoch, logs):
    #     # Use the model to predict the values from the test_images.
    #     test_pred_raw = model.predict(test_set_generator, step_size_validation)
    #     test_pred = np.argmax(test_pred_raw, axis=1)
    #
    #     # Calculate the confusion matrix using sklearn.metrics
    #     cm = confusion_matrix(test_set_generator.classes, test_pred)
    #
    #     figure = plot_confusion_matrix(cm, class_names=class_names)
    #     cm_image = plot_to_image(figure)
    #
    #     # Log the confusion matrix as an image summary.
    #     with file_writer_cm.as_default():
    #         tf.summary.image("Confusion Matrix", cm_image, step=epoch)
    #
    # # Define the per-epoch callback.
    # cm_callback = tf.keras.callbacks.LambdaCallback(on_epoch_end=log_confusion_matrix)

    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(montor='val_loss', factor=0.2, patience=5, min_lr=0.001)

    model.fit(training_set_generator, steps_per_epoch=step_size_train, epochs=number_of_epochs,
                        validation_data=test_set_generator, validation_steps=step_size_validation,
                        callbacks=[check_pointer, csv_logger, tensorboard_callback, reduce_lr])


def main():
    print("TensorFlow version: ", tf.__version__)
    assert version.parse(tf.__version__).release[0] >= 2, \
        "This code requires TensorFlow 2.0 or above."

    nclass = 13
    batch_size = 512
    model = build_cvred(input_shape=(7, 7, 14), n_output_classes=nclass)
    model.summary()
    tf.keras.utils.plot_model(model, show_shapes=True)

    macro_project_id = '1'
    dir_data = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    dataset_path = '/media/edel/MyFiles1/edel/Project_data2/dataset/'

    checkpoint_path = '/media/edel/MyFiles1/edel/Project_data2/dataset/model-checkpoints/'
    # input_checkpoint = '20201227-172734/CVRED_weights.57-1.62.hdf5'
    # model.load_weights(checkpoint_path + input_checkpoint)


    try:
        os.mkdir(checkpoint_path)
    except OSError:
        pass

    history_file_path = dataset_path + "training_log/"
    try:
        os.mkdir(history_file_path)
    except OSError:
        pass

    checkpoint_path = checkpoint_path + dir_data
    try:
        os.mkdir(checkpoint_path)
    except OSError:
        pass

    history_file_path = history_file_path + dir_data
    try:
        os.mkdir(history_file_path)
    except OSError:
        pass

    model_name = "CVRED"
    log_dir = dataset_path + "logs/fit/" + dir_data
    train_cvred(macro_project_id, model, target_size=(7, 7), batch_size=batch_size, dataset_path=dataset_path,
                training_path_prefix="train_set", testing_path_prefix="test_set",
                history_file_path=history_file_path,
                history_filename=model_name + ".csv", checkpoint_path=checkpoint_path,
                checkpoint_prefix=model_name, number_of_epochs=500,
                tensorboard_log_path=log_dir,
                )


if __name__ == "__main__":
    main()
