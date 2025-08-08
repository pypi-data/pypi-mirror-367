# horseracepredictor/core.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class HorseRacePredictor:
    def __init__(self, feature_cols, target_col='Winner'):
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.model = LinearRegression()
        self.trained = False

    def load_data(self, filepath):
        self.data = pd.read_csv(filepath)
        if not set(self.feature_cols + [self.target_col]).issubset(set(self.data.columns)):
            raise ValueError("Provided columns not found in CSV.")
        self.x = self.data[self.feature_cols]
        self.y = self.data[self.target_col]

    def train(self):
        self.model.fit(self.x, self.y)
        self.trained = True
        print("Model trained with coefficients:", self.model.coef_)

    def predict(self):
        if not self.trained:
            raise Exception("Model not trained. Call train() first.")
        return self.model.predict(self.x)

    def plot_predictions(self):
        if not self.trained:
            raise Exception("Model not trained.")
        predictions = self.model.predict(self.x)
        plt.scatter(self.x[self.feature_cols[0]], self.y, color='blue', label='Actual')
        plt.scatter(self.x[self.feature_cols[0]], predictions, color='red', label='Predicted')
        plt.xlabel(self.feature_cols[0])
        plt.ylabel(self.target_col)
        plt.legend()
        plt.title("Prediction vs Actual")
        plt.show()
