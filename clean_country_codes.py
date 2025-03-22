import pandas as pd

# Load the CSV file
file_path = "budget_data.csv"  # Update with your file path
df = pd.read_csv(file_path)

# Pivot the data
pivot_df = df.pivot_table(index=['Country Code', 'Country Name', 'Date'], 
                          columns='Budget Type', values='Cost', aggfunc='sum').reset_index()

# Rename columns
pivot_df.columns.name = None  # Remove column name
pivot_df = pivot_df.rename(columns={'Budget': 'Budget', 'Mid-Range': 'Mid-Range', 'Luxury': 'Luxury'})

# Fill NaN values with 0
pivot_df.fillna(0, inplace=True)

# Ensure cost columns are numeric (convert non-numeric values to NaN)
cost_columns = ['Budget', 'Mid-Range', 'Luxury']
pivot_df[cost_columns] = pivot_df[cost_columns].apply(pd.to_numeric, errors='coerce')

# Remove rows where all cost values are either NaN or 0
pivot_df = pivot_df[(pivot_df[cost_columns].notna().any(axis=1)) & (pivot_df[cost_columns].sum(axis=1) > 0)]
# Reorder columns to swap 'Mid-Range' and 'Luxury'
pivot_df = pivot_df[['Country Code', 'Country Name', 'Date', 'Budget', 'Mid-Range', 'Luxury']]

# Save to a new CSV file
output_file = "clean_budget_data.csv"
pivot_df.to_csv(output_file, index=False)

print(f"Processed data saved to {output_file}")
