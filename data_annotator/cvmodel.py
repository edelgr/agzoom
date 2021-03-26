from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import ELU
from tensorflow.keras.optimizers import Adam


def build_cvred(input_shape=(120, 120, 14), n_output_classes=10):
    modelo = Sequential()

    # bias_regularization = 0.0001
    # kernel_regularization = 0.0001

    # Convolution + Batch Norm. + ELU + Pooling #1
    modelo.add(Conv2D(32, (11, 11), input_shape=input_shape, activation='relu', strides=(1, 1), name="Conv1"))
    modelo.add(BatchNormalization(name="Conv1BN"))
    modelo.add(ELU(name="Conv1ELU"))
    modelo.add(MaxPooling2D(pool_size=(7, 7), strides=(2, 2), name="Conv1Pool"))

    # Convolution + Batch Norm. + ELU + Pooling #2
    modelo.add(Conv2D(48, (11, 11), input_shape=(52, 52, 32), activation='relu', strides=(1, 1), name="Conv2"))
    modelo.add(BatchNormalization(name="Conv2BN"))
    modelo.add(ELU(name="Conv2ELU"))
    modelo.add(MaxPooling2D(pool_size=(5, 5), strides=(2, 2), name="Conv2Pool"))

    # Convolution + Batch Norm. + ELU + Pooling #3
    modelo.add(Conv2D(64, (7, 7), input_shape=(19, 19, 48), activation='relu', strides=(1, 1), name="Conv3"))

    modelo.add(BatchNormalization(name="Conv3BN"))
    modelo.add(ELU(name="Conv3ELU"))
    modelo.add(MaxPooling2D(pool_size=(3, 3), strides=(1, 1), name="Conv3Pool"))

    # Convolution + Batch Norm. + ELU + Pooling #4
    modelo.add(Conv2D(80, (5, 5), activation='relu', strides=(1, 1), name="Conv4"))
    modelo.add(BatchNormalization(name="Conv4BN"))
    modelo.add(ELU(name="Conv4ELU"))
    modelo.add(MaxPooling2D(pool_size=(3, 3), strides=(1, 1), name="Conv4Pool"))  # Paper says (2,2) ?

    # Flattening
    modelo.add(Flatten())

    # FC #1
    modelo.add(Dense(units=1024, input_shape=(96,), activation='relu', ))
    modelo.add(ELU())
    modelo.add(Dropout(0.5))

    # # FC #2
    # modelo.add(Dense(units=96, input_shape=(2,), activation='relu'))

    # Output Layer
    modelo.add(Dense(units=n_output_classes, activation='softmax'))

    # Compile
    # sgd_optimizer = SGD(lr=0.002, decay=0.1 / 350, momentum=1)
    adam_optimizer = Adam()
    modelo.compile(optimizer=adam_optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return modelo


# prueba
print('hello')
