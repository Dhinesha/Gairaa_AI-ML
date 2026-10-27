import pandas as pd
import numpy as np
import shap
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

def train_and_explain_model(data_path: str, model_path: str):
    print("Loading cleaned dataset...")
    df = pd.read_csv(data_path)

    df['sales_class_binary'] = df['sales_class'].map({'HIGH SALES': 1, 'LOW SALES': 0})
    
    X = df.drop(['sales_class', 'sales_class_binary', 'total_amount'], axis=1)
    y = df['sales_class_binary']
    
    numeric_features = ['quantity', 'unit_price', 'discount', 'shipping_cost']
    categorical_features = ['region', 'category', 'customer_type', 'payment_method']
    
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=100, 
            max_depth=6, 
            min_samples_split=10, 
            min_samples_leaf=5, 
            random_state=42
        ))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training Random Forest model...")
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    print("\nModel Evaluation:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print(classification_report(y_test, y_pred))
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved successfully to {model_path}")
    

    print("\nGenerating Global SHAP Explanation...")
    
    rf_model = pipeline.named_steps['classifier']
    X_train_transformed = pipeline.named_steps['preprocessor'].transform(X_train)
    

    cat_encoder = pipeline.named_steps['preprocessor'].named_transformers_['cat']
    cat_feature_names = cat_encoder.get_feature_names_out(categorical_features)
    all_feature_names = numeric_features + list(cat_feature_names)
    

    readable_features = []
    for f in all_feature_names:
        if '_' in f and f.split('_')[0] in categorical_features:
            parts = f.split('_', 1)
            readable_features.append(f"{parts[0].replace('_', ' ').title()} = {parts[1]}")
        else:
            readable_features.append(f.replace('_', ' ').title())
            
    
    explainer = shap.TreeExplainer(rf_model)

    sample_size = min(500, X_train_transformed.shape[0])
    shap_values = explainer.shap_values(X_train_transformed[:sample_size])
    
    report_dir = r'D:\XAI_SHAP\explainable-sales-prediction\reports\figures'
    os.makedirs(report_dir, exist_ok=True)
    plt.figure()
    shap.summary_plot(shap_values[:, :, 1] if isinstance(shap_values, np.ndarray) else shap_values[1], X_train_transformed[:sample_size], feature_names=readable_features, show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(report_dir, 'shap_summary.png'))
    print(f"Saved SHAP summary plot to {report_dir}\\shap_summary.png")

if __name__ == '__main__':
    data_file = r'D:\XAI_SHAP\explainable-sales-prediction\data\cleaned_sales_data.csv'
    model_output = r'D:\XAI_SHAP\explainable-sales-prediction\models\sales_model.pkl'
    try:
        train_and_explain_model(data_file, model_output)
    except FileNotFoundError:
        print(f"Dataset not found at {data_file}. Please run the cleaning script first.")
