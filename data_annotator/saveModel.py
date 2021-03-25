import sys
import tensorflow as tf
import os
import json
import tempfile

sys.path.append('/home/edel/PycharmProjects/anotador')
from data_annotator.cvmodel2 import build_cvred

def main():
    macro_project_id = '5'
    project_data_path = '/media/edel/MyFiles1/edel/Project_data2/dataset/'
    input_checkpoint = 'model-checkpoints/20210321-030321/CVRED_weights.160-0.24.hdf5'
    checkpoint_path = project_data_path + input_checkpoint
    # input_class_indices = 'model-checkpoints/20201117-105006/CVRED_class_indices.json'
    # class_indices_path = project_data_path + 'macro_projects_data/' + macro_project_id + '/dataset_sentinel_unified/' + input_class_indices

    # checkpoint_path = '/media/edel/MyFiles1/edel/Project_data2/dataset/model-checkpoints/'

    # with open(class_indices_path) as f:
    #     class_indices = json.load(f)

    # nclass = len(class_indices)
    nclass = 13

    model = build_cvred(input_shape=(7, 7, 14), n_output_classes=nclass)
    model.load_weights(checkpoint_path)
    MODEL_DIR = tempfile.gettempdir()
    version = 1
    export_path = os.path.join(MODEL_DIR, str(version))
    print('export_path: ' + export_path)

    tf.keras.models.save_model(
        model,
        export_path,
        overwrite=True,
        include_optimizer=True,
        save_format=None,
        signatures=None,
        options=None
    )
    print('Saved model')
    os.environ["MODEL_DIR"] = MODEL_DIR

if __name__ == "__main__":
    main()
