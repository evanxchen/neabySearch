import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, Concatenate

# 假設的參數（根據你的資料調整）
timesteps = 24          # 例如過去 24 個月的資料
ts_feature_dim = 10     # 時間序列特徵數量（例如每月還款金額、餘額、rtn_cod 狀態數值化等）
static_feature_dim = 5  # 靜態特徵數量（例如 APPLY_AMT、LN_BAL、INT_RATE 等）

# 時間序列輸入
ts_input = Input(shape=(timesteps, ts_feature_dim), name='ts_input')
x_ts = LSTM(64, return_sequences=False, name='lstm_layer')(ts_input)
x_ts = Dropout(0.2, name='ts_dropout')(x_ts)

# 靜態特徵輸入
static_input = Input(shape=(static_feature_dim,), name='static_input')
x_static = Dense(32, activation='relu', name='static_dense')(static_input)

# 將兩部分資料融合
combined = Concatenate(name='concat_layer')([x_ts, x_static])
x = Dense(32, activation='relu', name='dense_1')(combined)
x = Dropout(0.2, name='dropout_1')(x)

# 輸出層：使用 sigmoid 輸出 0~1 的機率（分類任務）
output = Dense(1, activation='sigmoid', name='output')(x)

# 建立模型
model = Model(inputs=[ts_input, static_input], outputs=output)

# 編譯模型，使用 binary_crossentropy 作為損失函數
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.summary()

# 範例：訓練模型
# 假設 X_ts_train 為時間序列訓練資料，其 shape 為 (samples, timesteps, ts_feature_dim)
# 假設 X_static_train 為靜態特徵訓練資料，其 shape 為 (samples, static_feature_dim)
# 假設 y_train 為二元標籤，形狀為 (samples, 1)
#
# history = model.fit([X_ts_train, X_static_train], y_train,
#                     epochs=50, batch_size=64, validation_split=0.2)
