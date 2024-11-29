import pandas as pd

# File names in the same directory
csv_file_name = "Coursera.csv"  # Dataset file name
pkl_file_name = "courses.pkl"   # Pickle file name

# Step 1: Load the CSV file into a DataFrame
data = pd.read_csv(csv_file_name)

# Step 2: Save the DataFrame as a pickle file
data.to_pickle(pkl_file_name)

print(f"Data from {csv_file_name} has been saved to {pkl_file_name}")
