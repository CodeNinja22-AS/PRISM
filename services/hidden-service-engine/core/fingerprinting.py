import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
import warnings

# Suppress warnings for cleaner output during demonstration
warnings.filterwarnings('ignore')

class FeatureExtractor:
    """Extracts statistical features from raw network traces."""
    
    @staticmethod
    def extract(packet_sizes, timings):
        """
        Converts a raw traffic trace into a fixed-size feature vector.
        """
        if not packet_sizes or not timings:
            return np.zeros(10)
            
        sizes = np.array(packet_sizes)
        times = np.array(timings)
        
        # Inter-arrival times (IAT)
        iat = np.diff(times) if len(times) > 1 else np.array([0])
        
        features = [
            np.mean(sizes),             # Mean packet size
            np.std(sizes),              # Std dev of packet sizes
            np.max(sizes),              # Max packet size
            np.percentile(sizes, 75),   # 75th percentile size
            np.sum(sizes),              # Total volume
            np.mean(iat),               # Mean IAT
            np.std(iat),                # Std dev of IAT
            np.max(iat),                # Max IAT
            np.percentile(iat, 75),     # 75th percentile IAT
            len(sizes)                  # Packet count
        ]
        
        # Replace NaNs with 0
        return np.nan_to_num(np.array(features))

class LongitudinalProfile:
    """
    Aggregates multiple traces over time to create a robust, 
    noise-resistant longitudinal feature profile.
    """
    def __init__(self, profile_id):
        self.profile_id = profile_id
        self.traces = []
        
    def add_trace(self, packet_sizes, timings):
        self.traces.append((packet_sizes, timings))
        
    def get_aggregated_features(self):
        """
        Calculates features for all traces and returns the median feature vector
        to filter out anomalous/noisy single observations.
        """
        if not self.traces:
            return np.zeros(10)
            
        feature_matrix = []
        for sizes, times in self.traces:
            feat = FeatureExtractor.extract(sizes, times)
            feature_matrix.append(feat)
            
        # Use median across all traces to reduce the impact of outliers/noise
        return np.median(feature_matrix, axis=0)

class TrafficFingerprinter:
    """
    PHASE 6: Traffic Fingerprinting Engine
    Classifies traffic profiles using ML models.
    """
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
        self.is_trained = False
        self.classes = []

    def train(self, X, y):
        """Trains both Random Forest and XGBoost classifiers."""
        self.classes = list(set(y))
        
        # Train Random Forest
        self.rf_model.fit(X, y)
        
        # XGBoost requires numeric labels, map them
        self.label_map = {val: idx for idx, val in enumerate(self.classes)}
        self.inverse_label_map = {idx: val for val, idx in self.label_map.items()}
        y_numeric = np.array([self.label_map[label] for label in y])
        
        # Train XGBoost
        self.xgb_model.fit(np.array(X), y_numeric)
        
        self.is_trained = True
        
    def predict(self, feature_vector):
        """Predicts the fingerprint class using ensemble/voting (Simplified to show both)."""
        if not self.is_trained:
            raise Exception("Models must be trained before prediction.")
            
        feat_array = np.array(feature_vector).reshape(1, -1)
        
        # Random Forest Prediction
        rf_pred = self.rf_model.predict(feat_array)[0]
        rf_prob = np.max(self.rf_model.predict_proba(feat_array))
        
        # XGBoost Prediction
        xgb_pred_numeric = self.xgb_model.predict(feat_array)[0]
        xgb_pred = self.inverse_label_map[xgb_pred_numeric]
        xgb_prob = np.max(self.xgb_model.predict_proba(feat_array))
        
        return {
            "RandomForest": {"class": rf_pred, "confidence": rf_prob},
            "XGBoost": {"class": xgb_pred, "confidence": xgb_prob}
        }

if __name__ == "__main__":
    print("--- Building Phase 6 Models ---")
    
    # 1. Generate Synthetic Training Data (e.g., historical known traffic)
    X_train = []
    y_train = []
    
    # Class: Tor Hidden Service (Simulated properties: smaller packets, specific timing)
    for _ in range(50):
        sizes = np.random.normal(512, 100, 100)
        timings = np.cumsum(np.random.exponential(0.1, 100))
        X_train.append(FeatureExtractor.extract(sizes, timings))
        y_train.append("Tor_Hidden_Service")
        
    # Class: Standard HTTPS Web Browsing (Simulated properties: larger packets, bursty)
    for _ in range(50):
        sizes = np.random.normal(1200, 300, 100)
        timings = np.cumsum(np.random.exponential(0.5, 100))
        X_train.append(FeatureExtractor.extract(sizes, timings))
        y_train.append("Standard_HTTPS")
        
    # 2. Train the Fingerprinter
    fingerprinter = TrafficFingerprinter()
    fingerprinter.train(X_train, y_train)
    print("Models successfully trained (RandomForest, XGBoost).")

    # 3. Simulate a target being observed multiple times (Longitudinal Analysis)
    print("\n--- Longitudinal Observation (Target Alpha) ---")
    target_profile = LongitudinalProfile("Target_Alpha")
    
    # Add 5 traces for this target over time (They look like Tor traffic, but with noise)
    for i in range(1, 6):
        # Base signal (Tor-like) + Random noise
        sizes = np.random.normal(530, 120, 100) 
        timings = np.cumsum(np.random.exponential(0.12, 100))
        target_profile.add_trace(sizes, timings)
        print(f"Captured Trace {i}...")

    # 4. Extract Aggregated Features and Predict
    print("\nAggregating traces to filter noise...")
    robust_features = target_profile.get_aggregated_features()
    
    predictions = fingerprinter.predict(robust_features)
    
    print("\n--- Fingerprint Results ---")
    for model, result in predictions.items():
        print(f"{model} Prediction: {result['class']} (Confidence: {result['confidence']:.2%})")
