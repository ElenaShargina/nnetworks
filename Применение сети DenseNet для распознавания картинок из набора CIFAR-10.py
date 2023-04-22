# -*- coding: utf-8 -*-
"""Применение DenseNet для распознавания изображений

Automatically generated by Colaboratory.

# Применение сети DenseNet для распознавания картинок из набора CIFAR-10

Будет продемонстрирована работа предобученной сети DenseNet для распознавания картинок из набора CIFAR10.
Сверточная часть сети DenseNet будет первым слоем нашей модели, далее последуют наши собственные
полносвязные слои для классификации изображений по 10 классам. 

Обучение такой модели занимает очень много времени и на платформе colaboratory в рамках бесплатного аккаунта
его практически не запустить. Поэтому файл представлен как .py скрипт. Кроме того, прилагается файл с уже обученной
моделью (DenseNet+наши полносвязные слои), который скрипт будет использовать для экономии времени.

"""

import os.path

import numpy as np

from tensorflow.keras.datasets import cifar10

from tensorflow.keras.applications.densenet import DenseNet201
from tensorflow.keras.applications.densenet import preprocess_input, decode_predictions

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Flatten, Dropout, Lambda
from tensorflow.keras import utils, Input
import matplotlib.pyplot as plt

# фиксируем генератор случайных чисел
from numpy.random import seed
seed(2023)
from tensorflow.random import set_seed
set_seed(2023)

"""## Загрузка данных данных"""

# Загружаем тренировочные и тестовые данные из cifar10.
# Ширина и длина картинок в наборе - 32 пикселя.
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
width = 32
height = 32

# Названия классов из набора данных CIFAR-10
classes=['самолет', 'автомобиль',
         'птица', 'кот', 'олень', 'собака', 'лягушка', 'лошадь',
         'корабль', 'грузовик']

"""Просмотр примеров данных"""

plt.figure(figsize=(10,6))
for i in range(100,150):
    plt.subplot(5,10,i-100+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(x_train[i])
    plt.xlabel(classes[y_train[i][0]])
plt.show()

"""## Подготовка данных"""

x_train = preprocess_input(x_train)
x_test = preprocess_input(x_test)

# преобразуем ответы в one hot encoding
y_train = utils.to_categorical(y_train, 10)
y_test = utils.to_categorical(y_test, 10)

"""## Подготовка сети"""
# Обучение нашей модели занимает значительное количество времени (40 минут),
# поэтому воспользуемся уже сохраненной моделью.
file_model = 'mydensenet.h5'
if os.path.isfile(file_model):
    print('Файл с обученной сетью найден, загружаем.')
    model = load_model(file_model)
# если сохраненной модели не найдено, то делаем ее заново и сохраняем
else:
    print('Файл с обученной сетью не найден, будем собирать её заново.')
    # загружаем предварительно обученную нейронную сеть
    densenet = DenseNet201(weights='imagenet',
                                 include_top=False,
                                 input_shape=(width, height, 3))
    densenet.trainable = False
    densenet.summary()

    # Строим модель
    model = Sequential()
    # Предварительно обученную сеть загружаем как слой сети.
    # include_top=False убирает собственные квалификационные слои сети,
    # оставляя только сверточные до них. 
    model.add(densenet)
    # Добавляем слой, распрямляющий входные данные в вектор
    model.add(Flatten())

    # Добавляем полносвязный слой для нашей квалификации.
    model.add(Dense(512, activation='relu'))
    # Добавляем слой для защиты от переобучения
    model.add(Dropout(0.5))

    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    # На последнем полносвязном слое 10 нейронов по числу возможных классов изображений.
    model.add(Dense(10, activation='softmax'))

    model.summary()

    model.compile(loss='categorical_crossentropy',
                  optimizer="nadam",
                  metrics=['accuracy'])

    """## Обучаем нейронную сеть"""

    history = model.fit(x_train, y_train,
                        batch_size=64,
                        epochs=35,
                        validation_split=0.1,
                        verbose=2)

    model.save('mydensenet.h5')

"""## Проверка работы сети"""

print('Оценим работу модели на тестовых данных.')
scores = model.evaluate(x_test, y_test, verbose = 1)
print("Доля правильных ответов на тестовых данных, в процентах:", round(scores[1] * 100, 4))

# запустим работу сети на тестовых данных
results = model.predict(x_test)

# просмотрим результат работы для каких-то случайных картинок
# так как изображения уже обработаны для сети, они выглядят не так, как изначально
for n in [100,200,300,400,500]:
    plt.imshow(x_test[n])
    plt.show()
    print(f'Правильный ответ: {classes[np.argmax(y_test[n])]}')
    print(f'Ответ от нашей сети: {classes[np.argmax(results[n])]}')


