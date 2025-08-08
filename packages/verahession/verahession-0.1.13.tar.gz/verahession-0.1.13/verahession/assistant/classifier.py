import numpy as np
import pickle
from .utils import tokenize, stem, bag_of_words

class Classifier:
    def __init__(self, model_path):
        with open(model_path, 'rb') as f:
            data = pickle.load(f)

        self.all_words = data["all_words"]
        self.tags = data["tags"]

        self.W1 = data["W1"]
        self.b1 = data["b1"]
        self.W2 = data["W2"]
        self.b2 = data["b2"]

    def relu(self, x):
        return np.maximum(0, x)

    def softmax(self, x):
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / np.sum(e_x, axis=1, keepdims=True)

    def classify(self, sentence):
        tokens = tokenize(sentence)
        bag = bag_of_words(tokens, self.all_words)
        x = np.array([bag])  # Shape: (1, input_size)

        z1 = np.dot(x, self.W1) + self.b1
        a1 = self.relu(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        probs = self.softmax(z2)

        pred_idx = np.argmax(probs)
        confidence = probs[0][pred_idx]
        intent_tag = self.tags[pred_idx]

        return intent_tag, confidence
