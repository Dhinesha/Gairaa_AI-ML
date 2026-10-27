import pandas as pd
import numpy as np

def clean_sales_data(file_path: str, output_path: str):

    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    
    print("\nMissing values before cleaning:")
    print(df.isnull().sum())
    numerical_cols = ['quantity', 'unit_price', 'discount', 'shipping_cost', 'total_amount']
    categorical_cols = ['region', 'category', 'customer_type', 'payment_method', 'sales_class']
    

    for col in numerical_cols:
        if col in df.columns and df[col].isnull().any():
            median_value = df[col].median()
            df[col] = df[col].fillna(median_value)
            print(f"Filled missing values in '{col}' with median: {median_value:.2f}")


    for col in categorical_cols:
        if col in df.columns and df[col].isnull().any():
            mode_value = df[col].mode()[0]
            df[col] = df[col].fillna(mode_value)
            print(f"Filled missing values in '{col}' with mode: {mode_value}")
            
    print("\nMissing values after cleaning:")
    print(df.isnull().sum())
    
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nCleaned dataset saved successfully to {output_path}")
    
    return df

if __name__ == '__main__':

    input_file = r'D:\XAI_SHAP\explainable-sales-prediction\explainable_sales_5000.csv'
    output_file = r'D:\XAI_SHAP\explainable-sales-prediction\data\cleaned_sales_data.csv'
    
    try:
        cleaned_data = clean_sales_data(input_file, output_file)
        print("\nPreview of Cleaned Data:")
        print(cleaned_data.head())
    except FileNotFoundError:
        print(f"Error: Could not find the file at {input_file}. Please ensure the dataset exists.")
