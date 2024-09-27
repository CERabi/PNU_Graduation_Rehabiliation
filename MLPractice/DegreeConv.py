import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
import joblib

input = pd.read_csv("45.csv", encoding='cp949')
# print(input.iloc[-1,:])
angle_data = input.to_numpy()
input = pd.read_csv("90.csv", encoding='cp949')
angle_data = np.append(angle_data, input.to_numpy(), axis=0)
input = pd.read_csv("135.csv", encoding='cp949')
angle_data = np.append(angle_data, input.to_numpy(), axis=0)
input = pd.read_csv("180.csv", encoding='cp949')
angle_data = np.append(angle_data, input.to_numpy(), axis=0)
print(angle_data.shape)

X = angle_data[:,:-1]
y = angle_data[:,-1:]
print(X.shape)
print(y.shape)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
model = Ridge(alpha = 1, random_state = 42)
model.fit(X_train, y_train)
print(model.score(X_train, y_train))
print(model.score(X_test, y_test))

print(model.coef_)
print(model.intercept_)

# joblib.dump(model, 'rid_model.pkl')