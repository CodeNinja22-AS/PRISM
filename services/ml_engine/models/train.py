import os
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configure MLflow pointing to our local docker-compose container
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
mlflow.set_experiment("PRISM_Stylometry")

def train_model():
    print("[*] Loading training data...")
    # Load synthetic data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "../data/synthetic_authors.csv")
    df = pd.read_csv(data_path)
    
    X = df['text']
    y = df['author_id']
    
    # Stratify is not possible with so few samples, so simple split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("[-] Starting MLflow run...")
    with mlflow.start_run():
        # Pipeline: TF-IDF on character n-grams -> Logistic Regression
        # Char n-grams are excellent for capturing subconscious writing styles
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(analyzer='char', ngram_range=(2, 4), max_features=5000)),
            ('clf', LogisticRegression(random_state=42, max_iter=1000))
        ])
        
        print("[-] Training model...")
        pipeline.fit(X_train, y_train)
        
        # Evaluate
        predictions = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"[+] Model accuracy: {accuracy:.2f}")
        
        # Log parameters, metrics, and model to MLflow
        mlflow.log_param("ngram_range", "(2, 4)")
        mlflow.log_param("analyzer", "char")
        mlflow.log_metric("accuracy", accuracy)
        
        mlflow.sklearn.log_model(
            sk_model=pipeline,
            artifact_path="stylometry_model",
            registered_model_name="Stylometry_CharNGram"
        )
        print("[+] Model saved and registered in MLflow.")

if __name__ == "__main__":
    train_model()
