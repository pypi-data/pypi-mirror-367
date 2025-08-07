# horseracepredictor/predictor.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

class HorseRacePredictor:
    def __init__(self):
        self.weights = None
        self.biases = None
        self.model = None
        self.learning_rate = 0.02
        self.iterations = 20

    def load_data(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.x = self.data[['saddle', 'decimalPrice', 'runners', 'weight']]
        self.y = self.data['Winner']

    def linear_regression(self):
        reg = LinearRegression()
        reg.fit(self.x, self.y)
        self.model = reg
        return reg.coef_, reg.intercept_

    def logistic_regression(self):
        log_model = sm.Logit(self.y, self.x)
        result = log_model.fit(disp=0)
        self.model = result
        return result.summary()

    def compute_targets(self):
        self.targets = (
            -0.00044618449 * self.x['saddle']
            + 0.963206007 * self.x['decimalPrice']
            + 0.000387599664 * self.x['runners']
            - 0.0000333688539 * self.x['weight']
            - 0.014001054804715737
        ).values.reshape(-1, 1)
        return self.targets

    def init_weights(self):
        self.weights = np.random.uniform(0, 0.1, size=(4, 1))
        self.biases = np.random.uniform(0, 0.1, size=1)

    def train_model(self):
        observations = self.x.shape[0]
        self.init_weights()
        targets_2d = self.compute_targets()

        for _ in range(self.iterations):
            outputs = np.dot(self.x, self.weights) + self.biases
            deltas = outputs - targets_2d
            loss = np.sum(deltas ** 2) / (2 * observations)

            deltas_scaled = deltas / observations
            self.weights -= self.learning_rate * np.dot(self.x.T, deltas_scaled)
            self.biases -= self.learning_rate * np.sum(deltas_scaled)

        return self.weights, self.biases

    def predict(self, threshold=0.35):
        outputs = np.dot(self.x, self.weights) + self.biases
        predicted = (outputs.flatten() >= threshold).astype(int)
        return predicted

    def evaluate(self, predicted):
        actual = self.y[:len(predicted)].astype(int)
        correct = (predicted == actual).sum()
        return {
            "total": len(predicted),
            "correct": correct,
            "accuracy": correct / len(predicted)
        }
