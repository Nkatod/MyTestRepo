# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 10:53:57 2020

@author: User
"""

_rnnD = 30
thresholdForCity = 0.6

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import os
import math



from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import RandomizedSearchCV

from keras.models import Sequential
from keras import layers
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.wrappers.scikit_learn import KerasClassifier
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM


# Prepairing dataset

dataset = pd.ExcelFile('Untitled spreadsheet.xlsx').parse('Sheet1')

x_Dataset = dataset.iloc[:, 0].values
y_Dataset = dataset.iloc[:, 1].values

x_train = []
y_train = []

for i in range(len(x_Dataset)):
    strx = x_Dataset[i]
    stry = y_Dataset[i]
    x_train += list(strx)
    startSymbol = 0
    endSymbol = 0
    if type(stry) == type(''):
        startSymbol = strx.find(stry)
        endSymbol = strx.find(stry)+len(stry)
    for j in range(len(strx)):
        if j >= startSymbol and j < endSymbol:
            y_train.append(1)
            # res = 1
        else:
            y_train.append(0)
            # res = 0
        # print(strx[j]+' '+str(res))    


# encoder = LabelEncoder()
# x_train = encoder.fit_transform(x_train)
# print(x_train)
# encoder = OneHotEncoder(sparse=False)
# x_train = x_train.reshape((len(x_train), 1))
# encoder.fit_transform(x_train)
maxlen = 100
tokenizer = Tokenizer(num_words=5000, filters='~\t\n',lower=False, split=None, char_level=False, oov_token=None)
tokenizer.fit_on_texts(x_train)
x_train = tokenizer.texts_to_sequences(x_train)
x_train = pad_sequences(x_train, padding='post', maxlen=1)
y_train = np.array(y_train)
y_train = np.reshape(y_train, (y_train.shape[0], 1))

vocab_size = len(tokenizer.word_index) + 1
embedding_dim = 50

X_trainForRNN = []
y_trainForRNN = []
for i in range(_rnnD, len(x_train)):
    X_trainForRNN.append(x_train[i-_rnnD:i])    
    y_trainForRNN.append(y_train[i-_rnnD:i]) 
    
X_trainForRNN, y_trainForRNN = np.array(X_trainForRNN), np.array(y_trainForRNN)    
X_trainForRNN = np.reshape(X_trainForRNN, (X_trainForRNN.shape[0], X_trainForRNN.shape[1]))
y_trainForRNN = np.reshape(y_trainForRNN, (y_trainForRNN.shape[0], y_trainForRNN.shape[1]))

regressor = Sequential()
#first layer
regressor.add(layers.Embedding(vocab_size, embedding_dim, input_length=_rnnD))
regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))
#second layer
regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))
#third layer
regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))
#4-th layer
regressor.add(LSTM(units = 50, return_sequences = False))
regressor.add(Dropout(0.2))
# output
regressor.add(Dense(units = _rnnD, activation='sigmoid'))
#Compile
regressor.compile(optimizer = 'adam',
                  loss = 'binary_crossentropy',
                  metrics = ['accuracy'])
# Fitting
history = regressor.fit(X_trainForRNN, y_trainForRNN, epochs = 20, batch_size = 100)
loss, accuracy = regressor.evaluate(X_trainForRNN, y_trainForRNN, verbose=False)
print("Training Accuracy: {:.4f}".format(accuracy))

teststrOriginal = 	'​Привезите это в г. Мурманск нет лучше в г. Москву'
teststr = list(teststrOriginal)
x_test = tokenizer.texts_to_sequences(teststr)
x_test = pad_sequences(x_test, padding='post', maxlen=1)
x_testForRNN = []
for i in range(_rnnD, len(x_test)):
    x_testForRNN.append(x_test[i-_rnnD:i])    
    
x_testForRNN = np.array(x_testForRNN)  
x_testForRNN = np.reshape(x_testForRNN, (x_testForRNN.shape[0], x_testForRNN.shape[1]))

predicted = regressor.predict(x_testForRNN)
sumLst = []
for i in range(len(predicted)):
    sumLst.append(sum(predicted[i]))

lst = np.array(x_testForRNN[sumLst.index(max(sumLst))])
lst = np.reshape(lst, (lst.shape[0], 1))
lst = tokenizer.sequences_to_texts(lst)
resultCity = ''
resultProc = 0.00
countProc = 1
for i in range(len(predicted[sumLst.index(max(sumLst))])):
    if predicted[sumLst.index(max(sumLst))][i] > thresholdForCity:
        #print(lst[i]+' / ' +str(predicted[sumLst.index(max(sumLst))][i]))
        countProc += 1
        resultProc = (resultProc + predicted[sumLst.index(max(sumLst))][i])
        if lst[i] == '':
            resultCity += ' '
        else:
            resultCity += lst[i]

print('Введите адрес: ' + teststrOriginal)
print('Предположительно город: ('+ str(round((resultProc/countProc)*100, 1))+'%)'+ resultCity)
