from forecast import load_and_process_data, train_and_predict

data_file_path = 'grafana_data_process.csv'

# Load and process data
series = load_and_process_data(data_file_path)

# Train and predict
predictions = train_and_predict(series)

# Output all predictions
for i, pred in enumerate(predictions):
    print(f'[{i}] predicted={int(pred)}')
