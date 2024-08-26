import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

# Load the dataset
csv_file_path = './data/winequality-red.csv'
df = pd.read_csv(csv_file_path, delimiter=';')

# Features and target variable
X = df.drop('quality', axis=1)
y = df['quality']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Convert to TensorFlow tensors
X_train_tf = tf.constant(X_train_scaled, dtype=tf.float32)
y_train_tf = tf.constant(y_train.values, dtype=tf.float32)
X_test_tf = tf.constant(X_test_scaled, dtype=tf.float32)
y_test_tf = tf.constant(y_test.values, dtype=tf.float32)

# Define the model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train_tf.shape[1],)),
    tf.keras.layers.Dense(1)  # Linear regression layer
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train_tf, y_train_tf, epochs=100, verbose=1)

# Make predictions
y_pred_tf = model.predict(X_test_tf).flatten()

# Evaluate the model
mse = mean_squared_error(y_test, y_pred_tf)
print(f"Mean Squared Error: {mse}")

# Display the model's coefficients
weights = model.layers[0].get_weights()
print(f"Model weights: {weights[0].flatten()}")
print(f"Model bias: {weights[1]}")
