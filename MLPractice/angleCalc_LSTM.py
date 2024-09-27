import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# arm_correct_ 3개. 올바르게 한 경우. 총 25분 분량
# arm_wrong_ 2개. 올바르지 않은 경우. 총 40분 분량
import pandas as pd
data_correct = []
data_wrong = []
for i in [1,2,3]:
  data_correct.append(pd.read_csv("arm_correct_"+str(i)+".csv"))
for i in [1,2]:
  data_wrong.append(pd.read_csv("arm_wrong_"+str(i)+".csv"))

data_correct[2].tail()

timestep_n = 200

# 자투리 자르고 합치기
def cut_and_append(A, b, data, target):
    size = data.shape[0] // timestep_n
    cut = data.shape[0] % timestep_n

    new_A = np.append(A, data[:-cut])
    new_b = np.append(b, [target] * size)

    return new_A, new_b

# 데이터 합치기
X = np.array([])
y = np.array([])
for c in data_correct:
  X, y = cut_and_append(X,y,c.iloc[:,1:-1].to_numpy(), 1)
for c in data_wrong:
  X, y = cut_and_append(X,y,c.iloc[:,1:-1].to_numpy(), 0)

X = X.reshape(-1, timestep_n, 18)

print(X.shape)
print(y.shape)

# validation용으로 조금 나누기
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, stratify=y)

from keras.models import Sequential
from keras.layers import GRU, Dense

model2 = Sequential()
model2.add(GRU(units = 50, return_sequences = True, 
               input_shape = (200,18), activation = 'tanh'))
model2.add(GRU(units = 50, activation = 'tanh'))
model2.add(Dense(units = 2))
model2.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', 
               metrics = ['accuracy'])
#model2.summary()

earlystop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=30)
hist2 = model2.fit(X_train, y_train, epochs = 300, 
                      validation_split = 0.3, callbacks=[earlystop])

plt.plot(hist2.history['loss'], 'b-', alpha=0.6,label='loss')
plt.plot(hist2.history['val_loss'], 'r-', alpha=0.6,label='val_loss')
plt.xlabel('Epoch')
plt.legend()
plt.show()

plt.plot(hist2.history['accuracy'], 'g-', alpha=0.6,label='acc')
plt.plot(hist2.history['val_accuracy'], 'y-', alpha=0.6,label='val_acc')
plt.xlabel('Epoch')
plt.legend()
plt.show()

p = model2.predict(X_test)
print("test set 예측: ", p.argmax(axis=-1))
print("test set 실제: ", y_test.astype(int))

loss, acc = model2.evaluate(X_test, y_test)
print("loss, acc : ", loss, acc)