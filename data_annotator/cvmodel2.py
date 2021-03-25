from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import UpSampling2D
from tensorflow.keras.layers import Conv2DTranspose
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import ELU
from tensorflow.keras.optimizers import Adam


def build_cvred(input_shape=(7, 7, 14), n_output_classes=10):
    modelo = Sequential()

    modelo.add(UpSampling2D(input_shape=input_shape, interpolation='bilinear'))
    modelo.add(Conv2D(28, (3, 3), input_shape=(14, 14, 14), padding='same', activation='relu', strides=(1, 1), name="Conv1"))
    modelo.add(BatchNormalization(name="Conv1BN"))
    modelo.add(ELU(name="Conv1ELU"))

    modelo.add(Conv2D(48, (3, 3), input_shape=(14, 14, 28), activation='relu', strides=(1, 1), name="Conv2"))
    modelo.add(BatchNormalization(name="Conv2BN"))
    modelo.add(ELU(name="Conv2ELU"))

    modelo.add(Conv2DTranspose(64, (1, 1), input_shape=(13, 13, 48), activation='relu', strides=(2, 2), name="Conv3"))
    modelo.add(BatchNormalization(name="Conv3BN"))
    modelo.add(ELU(name="Conv3ELU"))

    modelo.add(Conv2D(80, (3, 3), input_shape=(26, 26, 64), padding='same', activation='relu', strides=(1, 1), name="Conv4"))
    modelo.add(BatchNormalization(name="Conv4BN"))
    modelo.add(ELU(name="Conv4ELU"))
    modelo.add(MaxPooling2D(pool_size=(2, 2), strides=(1, 1), name="Conv4Pool"))

    modelo.add(Conv2D(48, (3, 3), input_shape=(13, 13, 80), activation='relu', strides=(1, 1), name="Conv5"))
    modelo.add(BatchNormalization(name="Conv5BN"))
    modelo.add(ELU(name="Conv5ELU"))
    modelo.add(MaxPooling2D(pool_size=(2, 2), strides=(1, 1), name="Conv5Pool"))

    # Flattening
    modelo.add(Flatten())

    # FC #1
    modelo.add(Dense(units=128, input_shape=(1728,), activation='relu', ))
    modelo.add(ELU())
    modelo.add(Dropout(0.5))

    # Output Layer
    modelo.add(Dense(units=n_output_classes, activation='softmax'))

    # Compile
    # sgd_optimizer = SGD(lr=0.002, decay=0.1 / 350, momentum=1)
    adam_optimizer = Adam()
    modelo.compile(optimizer=adam_optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return modelo


