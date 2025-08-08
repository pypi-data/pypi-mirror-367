from horseracepredictor import HorseRacePredictor

# Create predictor object
predictor = HorseRacePredictor(
    feature_cols=['saddle', 'decimalPrice', 'runners', 'weight'],  # these must be in the CSV
    target_col='Winner'
)

# Load your race data CSV file
predictor.load_data('2019_Jan_Mar-4.csv')

# Train the model
predictor.train()

# Plot actual vs predicted values
predictor.plot_predictions()
