# -*- coding: utf-8 -*-
"""
Created on Wed May  6 20:29:08 2020

@author: User
"""



import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#Part 1 - Data preprocessing

dataset_train = pd.read_csv('covidItaly.csv')
training_set = dataset_train.iloc[:, 3:4].values
training_set = training_set[::-1] #reversing using list slicing

# Feature Scaling
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0,1))
training_set_scaled = sc.fit_transform(training_set)

X_train = []
y_train = []
RNNRange = 60
for i in range(RNNRange, len(training_set_scaled)):
    X_train.append(training_set_scaled[i-RNNRange:i, 0])
    y_train.append(training_set_scaled[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)

# Reshaping
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# Part 2 - Now let's make the RNN!
# Importing the Keras libraries and packages
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM

regressor = Sequential()
#first layer
regressor.add(LSTM(units = 100, return_sequences = True, input_shape =(X_train.shape[1],1)))
regressor.add(Dropout(0.2))
#second layer
regressor.add(LSTM(units = 100, return_sequences = True))
regressor.add(Dropout(0.2))
#third layer
regressor.add(LSTM(units = 100, return_sequences = True))
regressor.add(Dropout(0.2))
#4-th layer
regressor.add(LSTM(units = 100, return_sequences = False))
regressor.add(Dropout(0.2))
# output
regressor.add(Dense(units = 1))
#Compile
regressor.compile(optimizer = 'adam',
                  loss = 'mean_squared_error')
# Fitting
regressor.fit(X_train, y_train, epochs = 200, batch_size = 32)



#Visualization and predict

real_data = dataset_train.iloc[:, 3:4].values
real_data = real_data[::-1]


inputs = real_data
# inputs = inputs.reshape(-1,1)
inputs = sc.transform(inputs)

for j in range(30):
    X_test = []
    for i in range(RNNRange, len(inputs)):
        X_test.append(inputs[i-RNNRange:i, 0])
    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    predicted_data = regressor.predict(X_test)
    inputs = np.append(inputs, predicted_data[-1])
    inputs = np.reshape(inputs, [len(inputs),1])


predicted_data = sc.inverse_transform(predicted_data)

vis_predicted_data = []
for i in range(0, RNNRange):
    vis_predicted_data.append(real_data[i, 0])

for i in range(len(predicted_data)):
    vis_predicted_data.append(predicted_data[i, 0])

plt.plot(real_data, color = 'red', label = 'Real data')
plt.plot(vis_predicted_data, color = 'blue', label = 'Predicted')
plt.title('Covid')
plt.xlabel('Time')
plt.ylabel('Active cases')
plt.legend()
plt.show()









