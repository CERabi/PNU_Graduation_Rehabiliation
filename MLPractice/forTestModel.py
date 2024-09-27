import pandas as pd

from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping
import keras
from sklearn.model_selection import train_test_split
from keras.src.legacy.saving import legacy_h5_format

model = legacy_h5_format.load_model_from_hdf5("L20_D10_D1.h5")

input = pd.read_csv("data.csv", encoding='cp949')
X = input.loc[:, ['A_Ax', 'A_Ay', 'A_Az', 'A_Gx', 'A_Gy', 'A_Gz', 
              'B_Ax', 'B_Ay', 'B_Az', 'B_Gx', 'B_Gy', 'B_Gz']]
y = input.loc[:, ['angle']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# print(test[1])
y_pred = model.predict(X_test)
for i in range(30):
    print("예측 : {}, 실제 : {}".format(y_pred[i], y_test.iloc[i, 0]))

model.evaluate(X_train, y_train)