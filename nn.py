import tensorflow as tf
import numpy as np

# Example dataset
text = """
hello world. how are you today? hello again. the world is beautiful.
hello world. how are you today? hello again. the world is beautiful.
hello world. how are you today? hello again. the world is beautiful.
hello world. how are you today? hello again. the world is beautiful.
"""

# Create a vocabulary of unique characters
vocab = sorted(set(text))
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)

# Convert the text to integer indices
text_as_int = np.array([char2idx[c] for c in text])

# Define the maximum length of a sequence for training
seq_length = 10
examples_per_epoch = len(text) // (seq_length + 1)

# Create training examples and targets
char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)

# Generate sequences of the specified length
sequences = char_dataset.batch(seq_length + 1, drop_remainder=True)

# Split sequences into input and output
def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

dataset = sequences.map(split_input_target)

# Batch size
BATCH_SIZE = 64
# Buffer size to shuffle the dataset
BUFFER_SIZE = 10000
EPOCHS = 10

dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)
dataset = dataset.repeat()

# Define the model
vocab_size = len(vocab)
embedding_dim = 256
rnn_units = 1024

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(None,), batch_size=batch_size),
        tf.keras.layers.Embedding(vocab_size, embedding_dim),
        tf.keras.layers.GRU(rnn_units, return_sequences=True, stateful=True, recurrent_initializer='glorot_uniform'),
        tf.keras.layers.Dense(vocab_size)
    ])
    return model

model = build_model(vocab_size=len(vocab), embedding_dim=embedding_dim, rnn_units=rnn_units, batch_size=BATCH_SIZE)

def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

model.compile(optimizer='adam', loss=loss)

# Configure checkpoint saving
checkpoint_dir = './training_checkpoints'
checkpoint_prefix = checkpoint_dir + "/ckpt_{epoch}.weights.h5"

checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True,
    verbose=1
)

# Train the model
history = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])

# Save the entire model
model_save_path = './saved_model/my_model'
model.save(model_save_path)

# Reload the model
model = tf.keras.models.load_model(model_save_path)

# Rebuild the model with batch size 1 for text generation
model = build_model(vocab_size=len(vocab), embedding_dim=embedding_dim, rnn_units=rnn_units, batch_size=1)
model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
model.build(tf.TensorShape([1, None]))

def generate_text(model, start_string):
    num_generate = 1000  # Number of characters to generate
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)
    text_generated = []
    temperature = 1.0

    model.reset_states()
    for _ in range(num_generate):
        predictions = model(input_eval)
        predictions = tf.squeeze(predictions, 0)
        predictions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
        input_eval = tf.expand_dims([predicted_id], 0)
        text_generated.append(idx2char[predicted_id])

    return start_string + ''.join(text_generated)

print(generate_text(model, start_string="hello"))
