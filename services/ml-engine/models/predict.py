import os
import mlflow.sklearn

os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"

def predict_author(text: str) -> dict:
    """
    Loads the latest registered Stylometry model from MLflow and predicts the author.
    """
    model_name = "Stylometry_CharNGram"
    try:
        # Load the latest version of the model
        model_uri = f"models:/{model_name}/latest"
        model = mlflow.sklearn.load_model(model_uri)
    except Exception as e:
        print(f"[!] Error loading model from MLflow: {e}")
        return None

    # Predict
    prediction = model.predict([text])[0]
    
    # Get probabilities
    probas = model.predict_proba([text])[0]
    classes = model.classes_
    
    # Map classes to probabilities
    prob_dict = {cls: prob for cls, prob in zip(classes, probas)}
    
    return {
        "predicted_author": prediction,
        "confidence_scores": prob_dict
    }

if __name__ == "__main__":
    sample_text = "Greetings. I require a secure server. Kindly advise."
    print(f"[*] Analyzing text: '{sample_text}'")
    
    result = predict_author(sample_text)
    if result:
        print(f"[+] Predicted Author: {result['predicted_author']}")
        print(f"    Confidence: {result['confidence_scores'][result['predicted_author']]:.2f}")
