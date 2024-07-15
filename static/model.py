import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences

# Sample data (replace with your dataset)
texts = ["I love this movie", "This movie is terrible", "I hate people"]
labels = [0, 1, 1]  # 0 for appropriate, 1 for inappropriate

# Tokenize the input texts
tokenizer = Tokenizer()
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
maxlen = max(len(seq) for seq in sequences)
X = pad_sequences(sequences, maxlen=maxlen)

# Define the model architecture
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=64, input_length=maxlen),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Compile the model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
model.fit(X, labels, epochs=10, batch_size=1)

# Evaluate the model (if you have validation/test data)
# loss, accuracy = model.evaluate(X_val, y_val)
# print("Validation/Test Accuracy:", accuracy)
