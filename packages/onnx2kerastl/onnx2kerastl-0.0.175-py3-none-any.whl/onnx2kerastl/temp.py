import tensorflow as tf


m = tf.keras.models.load_model('/Users/idan/Downloads/dynamic_all.h5')

np.random.seed(0)
input1 = np.expand_dims(np.random.rand(256, 256, 1).astype("float32"), axis=0)
np.random.seed(1)
input2 = np.expand_dims(np.random.rand(1112, 1936, 1).astype("float32"), axis=0)
np.random.seed(2)
input3 = np.expand_dims(np.random.rand( 1, 1, 2).astype("float32"), axis=0)

