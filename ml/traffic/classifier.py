import numpy as np
import pickle
from datetime import datetime
from collections import deque
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("WARNING: scikit-learn is not installed. Traffic Classifier will run in mock mode.")

class TrafficClassifier:
    """
    Advanced ML Traffic Fingerprinting
    Classifies raw packet statistics into traffic types (Streaming, Chat, Web, P2P).
    Uses Random Forest which is excellent for tabular/statistical network features.
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42) if SKLEARN_AVAILABLE else None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        
        # Mapping numerical classes back to labels
        self.labels = {0: "Web Browsing", 1: "Video Streaming", 2: "Secure Chat", 3: "File Transfer/P2P"}
        
    def _extract_features(self, packet_sizes, packet_times):
        """
        Extracts statistical features from raw packet data.
        In a real scenario, this takes a PCAP. Here we take arrays.
        """
        if not len(packet_sizes) or len(packet_sizes) < 2:
            return np.zeros(10)
            
        inter_arrival = np.diff(packet_times)
        
        features = [
            np.mean(packet_sizes),
            np.std(packet_sizes),
            np.max(packet_sizes),
            np.min(packet_sizes),
            np.median(packet_sizes),
            np.mean(inter_arrival) if len(inter_arrival) > 0 else 0,
            np.std(inter_arrival) if len(inter_arrival) > 0 else 0,
            np.max(inter_arrival) if len(inter_arrival) > 0 else 0,
            len(packet_sizes) / (packet_times[-1] - packet_times[0] + 0.001), # Packets per second
            sum(packet_sizes) / (packet_times[-1] - packet_times[0] + 0.001)  # Bytes per second
        ]
        return np.array(features)

    def train(self, X_raw, y):
        """Trains the model. X_raw is a list of (packet_sizes, packet_times) tuples."""
        if not SKLEARN_AVAILABLE:
            self.is_trained = True
            print("[Mock] Trained model on synthetic data.")
            return

        X_features = np.array([self._extract_features(sizes, times) for sizes, times in X_raw])
        X_scaled = self.scaler.fit_transform(X_features)
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
    def predict(self, packet_sizes, packet_times):
        """Predicts the traffic type and returns probabilities."""
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
            
        if not SKLEARN_AVAILABLE:
            # Mock prediction
            import random
            pred_class = random.choice(list(self.labels.keys()))
            probs = {self.labels[i]: (0.8 if i == pred_class else 0.06) for i in self.labels}
            return self.labels[pred_class], probs
            
        features = self._extract_features(packet_sizes, packet_times).reshape(1, -1)
        scaled_features = self.scaler.transform(features)
        
        pred = self.model.predict(scaled_features)[0]
        prob_array = self.model.predict_proba(scaled_features)[0]
        
        probs = {self.labels[i]: float(prob_array[i]) for i in range(len(self.labels))}
        
        return self.labels[pred], probs


class ProfileTracker:
    """
    Longitudinal Traffic Fingerprinting
    Tracks a user's traffic behavior vector over time to detect profile drift.
    """
    def __init__(self, history_size=10):
        self.history = deque(maxlen=history_size)
        self.baseline_vector = None
        
    def update_profile(self, feature_vector):
        """Adds a new observation and updates the baseline (moving average)."""
        self.history.append(np.array(feature_vector))
        # Baseline is the mean of recent history
        self.baseline_vector = np.mean(self.history, axis=0)
        
    def check_drift(self, new_feature_vector):
        """
        Calculates cosine similarity between new observation and baseline.
        Returns a drift score (0 = no drift, 1 = total drift/different user).
        """
        if self.baseline_vector is None:
            return 0.0 # No history to compare against
            
        vec1 = self.baseline_vector
        vec2 = np.array(new_feature_vector)
        
        # Cosine similarity
        dot = np.dot(vec1, vec2)
        norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        if norm == 0:
            return 0.0
            
        similarity = dot / norm
        drift_score = 1.0 - similarity
        return max(0.0, drift_score)


if __name__ == "__main__":
    print("--- ML TRAFFIC CLASSIFIER & LONGITUDINAL TRACKING ---")
    
    # Generate Synthetic Data for demonstration
    print("\n[1] Generating Synthetic Tor Traffic Dataset...")
    np.random.seed(42)
    
    # Class 0: Web (bursty, small/medium packets)
    # Class 1: Video (steady high volume, large packets)
    X_train = []
    y_train = []
    
    for _ in range(50):
        # Web
        sizes = np.random.randint(40, 1500, size=50)
        times = np.cumsum(np.random.exponential(0.1, size=50))
        X_train.append((sizes, times))
        y_train.append(0)
        
        # Video
        sizes = np.random.randint(1000, 1500, size=200)
        times = np.cumsum(np.random.exponential(0.01, size=200))
        X_train.append((sizes, times))
        y_train.append(1)

    classifier = TrafficClassifier()
    print("[2] Training Random Forest Classifier on traffic statistics...")
    classifier.train(X_train, y_train)
    
    print("[3] Live Classification Test:")
    test_sizes = np.random.randint(1200, 1500, size=150) # Looks like video
    test_times = np.cumsum(np.random.exponential(0.01, size=150))
    
    predicted_label, probabilities = classifier.predict(test_sizes, test_times)
    print(f"  -> Predicted Activity: {predicted_label}")
    print(f"  -> Confidence Distribution: {probabilities}")
    
    print("\n[4] Longitudinal Profile Tracking:")
    tracker = ProfileTracker()
    
    # User behaves normally for 5 sessions
    print("  Updating profile with 5 normal sessions...")
    for _ in range(5):
        tracker.update_profile(classifier._extract_features(test_sizes, test_times))
        
    # Suddenly user behavior changes completely (e.g. account hijacked or different usage)
    web_sizes = np.random.randint(40, 500, size=20)
    web_times = np.cumsum(np.random.exponential(0.5, size=20))
    abnormal_features = classifier._extract_features(web_sizes, web_times)
    
    drift = tracker.check_drift(abnormal_features)
    print(f"  -> New Session Drift Score: {drift:.2f} (0=Normal, 1=Complete Change)")
    if drift > 0.3:
        print("  -> ALERT: Significant longitudinal profile drift detected! Possible identity change.")
