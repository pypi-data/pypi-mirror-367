import json
import numpy as np
import pickle
from .utils import tokenize, stem, bag_of_words
from .model import *

class NeuralNetNumpy:
    def __init__(self, input_size, hidden_size, output_size, lr=0.001):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lr = lr

        # Xavier Initialization
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2. / input_size)
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2. / hidden_size)
        self.b2 = np.zeros((1, output_size))

    def relu(self, x):
        return np.maximum(0, x)

    def relu_derivative(self, x):
        return (x > 0).astype(float)

    def softmax(self, x):
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / np.sum(e_x, axis=1, keepdims=True)

    def forward(self, x):
        self.z1 = np.dot(x, self.W1) + self.b1
        self.a1 = self.relu(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2

    def compute_loss(self, y_pred, y_true):
        m = y_true.shape[0]
        log_likelihood = -np.log(y_pred[range(m), y_true])
        loss = np.sum(log_likelihood) / m
        return loss

    def backward(self, x, y_true):
        m = y_true.shape[0]

        dz2 = self.a2
        dz2[range(m), y_true] -= 1
        dz2 /= m

        dW2 = np.dot(self.a1.T, dz2)
        db2 = np.sum(dz2, axis=0, keepdims=True)

        da1 = np.dot(dz2, self.W2.T)
        dz1 = da1 * self.relu_derivative(self.z1)
        dW1 = np.dot(x.T, dz1)
        db1 = np.sum(dz1, axis=0, keepdims=True)

        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2

class trainer:
    def __init__(self, INTENTS_PATH, MODEL_SAVE):
        self.INTENTS_PATH = INTENTS_PATH
        self.MODEL_FILE = MODEL_SAVE

    def train(self):
        with open(self.INTENTS_PATH, 'r') as f:
            intents = json.load(f)

        all_words = []
        tags = []
        xy = []

        for intent in intents['intents']:
            tag = intent['tag']
            tags.append(tag)
            for pattern in intent['patterns']:
                w = tokenize(pattern)
                all_words.extend(w)
                xy.append((w, tag))

        ignore_words = ['?', '.', '!', ',']
        all_words = sorted(set(stem(w) for w in all_words if w not in ignore_words))
        tags = sorted(set(tags))

        X_train = []
        y_train = []

        for (pattern_sentence, tag) in xy:
            bag = bag_of_words(pattern_sentence, all_words)
            X_train.append(bag)
            y_train.append(tags.index(tag))

        X_train = np.array(X_train)
        y_train = np.array(y_train)

        batch_size = 8
        hidden_size = 8
        output_size = len(tags)
        input_size = len(all_words)
        learning_rate = 0.001

        num_patterns = sum(len(intent['patterns']) for intent in intents['intents'])
        complexity_factor = len(tags) * len(all_words)
        num_epochs = min(1500, max(300, int((num_patterns * 10) + (complexity_factor / 3))))

        model = NeuralNetNumpy(input_size, hidden_size, output_size, lr=learning_rate)

        for epoch in range(num_epochs):
            indices = np.random.permutation(len(X_train))
            X_train_shuffled = X_train[indices]
            y_train_shuffled = y_train[indices]

            for i in range(0, len(X_train), batch_size):
                x_batch = X_train_shuffled[i:i+batch_size]
                y_batch = y_train_shuffled[i:i+batch_size]

                y_pred = model.forward(x_batch)
                loss = model.compute_loss(y_pred, y_batch)
                model.backward(x_batch, y_batch)

            if (epoch + 1) % 100 == 0 or epoch == num_epochs - 1:
                print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss:.4f}")

        data = {
            "W1": model.W1,
            "b1": model.b1,
            "W2": model.W2,
            "b2": model.b2,
            "input_size": input_size,
            "hidden_size": hidden_size,
            "output_size": output_size,
            "all_words": all_words,
            "tags": tags,
            "responses": {intent['tag']: intent.get('responses', []) for intent in intents['intents']},
            "commands": {intent['tag']: intent.get('command', None) for intent in intents['intents']},
        }

        with open(self.MODEL_FILE, 'wb') as f:
            pickle.dump(data, f)

        print(f"Model trained and saved to {self.MODEL_FILE}")
