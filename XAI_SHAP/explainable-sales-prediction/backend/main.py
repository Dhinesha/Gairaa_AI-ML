from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import shap

app = FastAPI(title="Explainable Sales Prediction API")


def generate_human_explanation(prediction_label: str, probability: float, explanation: list, input_data: dict) -> dict:
    """Generate a plain-English explanation that any human can understand."""
    
    positive_factors = [e for e in explanation if e["shap_value"] > 0]
    negative_factors = [e for e in explanation if e["shap_value"] < 0]
    
    # Sort by absolute impact
    positive_factors.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    negative_factors.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    
    confidence = "high" if probability > 0.75 or probability < 0.25 else "moderate" if probability > 0.6 or probability < 0.4 else "low"
    prob_pct = round(probability * 100)
    
    # Build the summary sentence
    if prediction_label == "HIGH SALES":
        summary = f"The model predicts this transaction will result in HIGH SALES with {confidence} confidence ({prob_pct}%)."
    else:
        summary = f"The model predicts this transaction will result in LOW SALES with {confidence} confidence ({100 - prob_pct}% chance of low sales)."
    
    # Helper to describe a feature's value in plain English
    def describe_feature(feat):
        name = feat["feature"]
        val = feat["value"]
        strength = abs(feat["shap_value"])
        
        if strength > 0.1:
            intensity = "strongly"
        elif strength > 0.03:
            intensity = "moderately"
        elif strength > 0.01:
            intensity = "slightly"
        else:
            intensity = "marginally"
        
        # Clean up feature names for readability
        clean_name = name.replace(" = ", ": ").replace("_", " ")
        
        # Build a natural sentence based on feature type
        if "quantity" in name.lower():
            return f"A quantity of {val} units {intensity} pushes the prediction"
        elif "unit price" in name.lower():
            return f"A unit price of ₹{val} {intensity} influences the prediction"
        elif "discount" in name.lower():
            return f"A {val}% discount {intensity} affects the outcome"
        elif "shipping" in name.lower():
            return f"A shipping cost of ₹{val} {intensity} impacts the result"
        elif "region" in name.lower():
            region_val = val if val else name.split("=")[-1].strip() if "=" in name else name
            return f"Being in the {region_val} region {intensity} influences the prediction"
        elif "category" in name.lower():
            cat_val = val if val else name.split("=")[-1].strip() if "=" in name else name
            return f"The {cat_val} product category {intensity} affects the outcome"
        elif "customer" in name.lower():
            cust_val = val if val else name.split("=")[-1].strip() if "=" in name else name
            return f"A {cust_val} customer type {intensity} influences the prediction"
        elif "payment" in name.lower():
            pay_val = val if val else name.split("=")[-1].strip() if "=" in name else name
            return f"Payment via {pay_val} {intensity} affects the result"
        else:
            return f"{clean_name} ({val}) {intensity} affects the prediction"
    
    # Generate reason bullets
    reasons_for = []
    reasons_against = []
    
    for f in positive_factors[:5]:
        if abs(f["shap_value"]) > 0.005:
            desc = describe_feature(f)
            reasons_for.append(f"{desc} toward High Sales.")
    
    for f in negative_factors[:5]:
        if abs(f["shap_value"]) > 0.005:
            desc = describe_feature(f)
            reasons_against.append(f"{desc} toward Low Sales.")
    
    # Build the key takeaway
    if prediction_label == "HIGH SALES" and len(reasons_for) > 0:
        top = positive_factors[0]
        takeaway = f"The biggest reason for this prediction is: {describe_feature(top).lower()} toward high sales."
    elif prediction_label == "LOW SALES" and len(reasons_against) > 0:
        top = negative_factors[0]
        takeaway = f"The biggest reason for this prediction is: {describe_feature(top).lower()} toward low sales."
    else:
        takeaway = "Multiple small factors combined to produce this prediction."
    
    return {
        "summary": summary,
        "takeaway": takeaway,
        "confidence": confidence,
        "reasons_for_high_sales": reasons_for,
        "reasons_for_low_sales": reasons_against
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model_pipeline = joblib.load(r'D:\XAI_SHAP\explainable-sales-prediction\models\sales_model.pkl')
    rf_model = model_pipeline.named_steps['classifier']
    explainer = shap.TreeExplainer(rf_model)
    print("Model and SHAP explainer loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    model_pipeline = None

class SalesInput(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity sold must be positive")
    unit_price: float = Field(..., gt=0, description="Unit price must be positive")
    discount: float = Field(..., ge=0, le=100, description="Discount must be between 0 and 100")
    region: str
    category: str
    customer_type: str
    payment_method: str
    shipping_cost: float = Field(..., ge=0, description="Shipping cost cannot be negative")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Explainable Sales Prediction API! Visit /docs for the API documentation."}

@app.post("/predict")
def predict_sales(data: SalesInput):
    if model_pipeline is None:
        raise HTTPException(status_code=500, detail="Model is not loaded on the server.")
        
    input_data = pd.DataFrame([{
        "quantity": data.quantity,
        "unit_price": data.unit_price,
        "discount": data.discount,
        "region": data.region,
        "category": data.category,
        "customer_type": data.customer_type,
        "payment_method": data.payment_method,
        "shipping_cost": data.shipping_cost
    }])
    
    try:

        prediction_int = model_pipeline.predict(input_data)[0]
        probability = float(model_pipeline.predict_proba(input_data)[0][1])
        prediction_label = "HIGH SALES" if prediction_int == 1 else "LOW SALES"
        
        preprocessor = model_pipeline.named_steps['preprocessor']
        input_transformed = preprocessor.transform(input_data)
        
        shap_values = explainer.shap_values(input_transformed)
        if isinstance(shap_values, np.ndarray):
            class_1_shap = shap_values[0, :, 1]
        else:
            class_1_shap = shap_values[1][0]

        numeric_features = ['quantity', 'unit_price', 'discount', 'shipping_cost']
        categorical_features = ['region', 'category', 'customer_type', 'payment_method']
        cat_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
        all_feature_names = numeric_features + list(cat_feature_names)
        
        explanation = []
        for i, feature_name in enumerate(all_feature_names):
            shap_val = float(class_1_shap[i])
            if abs(shap_val) > 0.001:  
                
                readable_name = feature_name.replace('_', ' ').title()
                if '=' in readable_name or '_' in feature_name:
                    parts = feature_name.split('_', 1)
                    if len(parts) > 1 and parts[0] in categorical_features:
                        readable_name = f"{parts[0].replace('_', ' ').title()} = {parts[1]}"
                
                orig_val = ""
                if feature_name in input_data.columns:
                    orig_val = str(input_data.iloc[0][feature_name])
                elif '_' in feature_name:
                    orig_val = feature_name.split('_', 1)[1] 

                effect_label = "High Sales" if shap_val > 0 else "Low Sales"
                
                explanation.append({
                    "feature": readable_name,
                    "value": orig_val,
                    "shap_value": round(shap_val, 4),
                    "impact": effect_label
                })
        explanation.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        
        return {
            "prediction": prediction_label,
            "probability": round(probability, 4),
            "explanation": explanation,
            "human_explanation": generate_human_explanation(
                prediction_label, probability, explanation,
                input_data.iloc[0].to_dict()
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
