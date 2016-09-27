'''Train a simple deep CNN on the CIFAR10 small images dataset.
GPU run command:
    THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python cifar10_cnn.py
It gets down to 0.65 test logloss in 25 epochs, and down to 0.55 after 50 epochs.
(it's still underfitting at that point, though).
Note: the data was pickled with Python 2, and some encoding issues might prevent you
from loading it in Python 3. You might have to load it in Python 2,
save it in a different format, load it in Python 3 and repickle it.
'''

from __future__ import print_function
import numpy as np
# from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from keras.utils import np_utils
import os
import cv2

def load_data():
    dirname = "/home/qibai/Documents/smpData/images/"

    images = {}
    labels = {}
    lines = open("/home/qibai/Documents/smpData/communityDetect/label_maps.csv")
    for line in lines:
        items = line.strip().split(",")
        labels[items[0]] = items[2]
    for parent,dirnames,filenames in os.walk(dirname):
        for filename in filenames:
            if filename not in labels:
                print ("can't find user :" + filename)
                continue
            images[filename] = os.path.join(parent, filename)

    X_train = np.zeros((len(images), 180, 180, 3), dtype="uint8")
    y_train = np.zeros((len(images),), dtype="uint8")

    i = 0
    for key in images:
        try:
            X_train[i, :, :, :] = cv2.imread(images.get(key))
            y_train[i] = labels.get(key)
            i += 1
        except:
            print (key)

    # fpath = os.path.join(path, 'test_batch')
    # X_test, y_test = load_batch(fpath)
    #
    # y_train = np.reshape(y_train, (len(y_train), 1))
    # y_test = np.reshape(y_test, (len(y_test), 1))
    print ("")
    return (X_train, y_train)#, (X_test, y_test)

batch_size = 32
nb_classes = 3
nb_epoch = 60
data_augmentation = False

# input image dimensions
img_rows, img_cols = 180, 180
# the CIFAR10 images are RGB
img_channels = 3

# the data, shuffled and split between train and test sets
# (X_train, y_train), (X_test, y_test) = cifar10.load_data()
(X_train, y_train) = load_data()
print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
# print(X_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
Y_train = np_utils.to_categorical(y_train, nb_classes)
# Y_test = np_utils.to_categorical(y_test, nb_classes)

model = Sequential()

model.add(Convolution2D(32, 7, 7, border_mode='same',
                        input_shape=(img_rows, img_cols, img_channels), dim_ordering='tf'))
model.add(Activation('relu'))
model.add(Convolution2D(32, 7, 7))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))

model.add(Convolution2D(64, 7, 7, border_mode='same'))
model.add(Activation('relu'))
model.add(Convolution2D(64, 7, 7))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(nb_classes))
model.add(Activation('softmax'))

# let's train the model using SGD + momentum (how original).
sgd = SGD(lr=0.02, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])

X_train = X_train.astype('float32')
# X_test = X_test.astype('float32')
X_train /= 255
# X_test /= 255

if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(X_train, Y_train,
              batch_size=batch_size,
              nb_epoch=nb_epoch,
              # validation_data=(X_test, Y_test),
              validation_split=0.2,
              shuffle=True)
else:
    print('Using real-time data augmentation.')

    # this will do preprocessing and realtime data augmentation
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied)
    datagen.fit(X_train)

    # fit the model on the batches generated by datagen.flow()
    model.fit_generator(datagen.flow(X_train, Y_train,
                        batch_size=batch_size),
                        samples_per_epoch=X_train.shape[0],
                        nb_epoch=nb_epoch,
                        validation_data=())




