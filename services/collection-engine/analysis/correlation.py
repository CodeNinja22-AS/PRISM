import numpy as np
from scipy.stats import pearsonr, spearmanr
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

class TrafficCorrelationEngine:
    """
    PHASE 5: Traffic Correlation Engine
    Correlates abstracted network traces to determine if two controlled 
    observations represent the same communication.
    """
    
    def __init__(self):
        pass

    def _normalize(self, trace):
        """Normalizes a trace to 0-1 scale."""
        if not trace or max(trace) == min(trace):
            return np.zeros(len(trace))
        return (np.array(trace) - min(trace)) / (max(trace) - min(trace))

    def pearson_similarity(self, trace_a, trace_b):
        """Calculates Pearson correlation coefficient."""
        if len(trace_a) != len(trace_b):
            # Pad the shorter one with zeros for basic comparison if lengths differ
            max_len = max(len(trace_a), len(trace_b))
            trace_a = np.pad(trace_a, (0, max_len - len(trace_a)))
            trace_b = np.pad(trace_b, (0, max_len - len(trace_b)))
            
        # Add slight noise to avoid constant array warning in pearsonr
        trace_a = np.array(trace_a) + np.random.normal(0, 1e-10, len(trace_a))
        trace_b = np.array(trace_b) + np.random.normal(0, 1e-10, len(trace_b))
        
        corr, _ = pearsonr(trace_a, trace_b)
        return max(0.0, corr) # Map negative correlation to 0 for similarity score

    def spearman_similarity(self, trace_a, trace_b):
        """Calculates Spearman rank-order correlation coefficient."""
        if len(trace_a) != len(trace_b):
            max_len = max(len(trace_a), len(trace_a))
            trace_a = np.pad(trace_a, (0, max_len - len(trace_a)))
            trace_b = np.pad(trace_b, (0, max_len - len(trace_b)))
            
        corr, _ = spearmanr(trace_a, trace_b)
        # Handle nan if arrays are constant
        if np.isnan(corr):
            return 0.0
        return max(0.0, corr)

    def cross_correlation(self, trace_a, trace_b):
        """Calculates normalized cross-correlation."""
        a = self._normalize(trace_a)
        b = self._normalize(trace_b)
        
        if len(a) == 0 or len(b) == 0:
            return 0.0
            
        cc = np.correlate(a, b, mode='full')
        max_cc = np.max(cc)
        # Normalize by auto-correlation max to get a 0-1 score
        norm_factor = np.sqrt(np.sum(a**2) * np.sum(b**2))
        if norm_factor == 0:
            return 0.0
        return max(0.0, min(1.0, max_cc / norm_factor))

    def timing_similarity(self, timings_a, timings_b, threshold=0.1):
        """Calculates similarity based on inter-packet delays."""
        # Simplified: ratio of overlapping timestamps within a threshold
        if not timings_a or not timings_b:
            return 0.0
            
        matches = 0
        for t_a in timings_a:
            for t_b in timings_b:
                if abs(t_a - t_b) <= threshold:
                    matches += 1
                    break # One match per event
                    
        return min(1.0, matches / max(len(timings_a), len(timings_b)))

    def volume_similarity(self, vol_a, vol_b):
        """Calculates similarity based on total volume transferred."""
        total_a = sum(vol_a)
        total_b = sum(vol_b)
        
        if total_a == 0 and total_b == 0:
            return 1.0
        if total_a == 0 or total_b == 0:
            return 0.0
            
        diff = abs(total_a - total_b)
        max_vol = max(total_a, total_b)
        return 1.0 - (diff / max_vol)

    def dynamic_time_warping(self, trace_a, trace_b):
        """
        VERSION 2: Dynamic Time Warping (DTW)
        More robust sequence alignment that handles shifts in time.
        """
        if len(trace_a) == 0 or len(trace_b) == 0:
            return 0.0
            
        # Reshape for fastdtw
        a = np.array(trace_a).reshape(-1, 1)
        b = np.array(trace_b).reshape(-1, 1)
        
        distance, path = fastdtw(a, b, dist=euclidean)
        
        # Convert distance to similarity score (0 to 1)
        # Using a decay function: sim = 1 / (1 + distance)
        # Scaled by sequence length to be somewhat invariant to trace size
        max_len = max(len(trace_a), len(trace_b))
        normalized_distance = distance / max_len
        similarity = 1.0 / (1.0 + normalized_distance)
        return similarity

    def analyze(self, trace_a, trace_b, timings_a=None, timings_b=None):
        """
        Runs the full correlation suite and generates a report.
        trace_a/b are arrays of packet sizes or volume bins.
        """
        # If timings aren't provided, just use generic indices
        if timings_a is None:
            timings_a = list(range(len(trace_a)))
        if timings_b is None:
            timings_b = list(range(len(trace_b)))

        results = {
            "Pearson": self.pearson_similarity(trace_a, trace_b),
            "Spearman": self.spearman_similarity(trace_a, trace_b),
            "CrossCorrelation": self.cross_correlation(trace_a, trace_b),
            "TimingSimilarity": self.timing_similarity(timings_a, timings_b),
            "VolumeSimilarity": self.volume_similarity(trace_a, trace_b),
            "DTW": self.dynamic_time_warping(trace_a, trace_b)
        }
        
        # Calculate overall correlation score (weighted average)
        weights = {
            "Pearson": 0.1,
            "Spearman": 0.1,
            "CrossCorrelation": 0.2,
            "TimingSimilarity": 0.25,
            "VolumeSimilarity": 0.1,
            "DTW": 0.25
        }
        
        overall_score = sum(results[k] * weights[k] for k in weights)
        results["OverallCorrelationScore"] = overall_score
        
        return results

if __name__ == "__main__":
    # Example Usage / Test
    engine = TrafficCorrelationEngine()
    
    # Generate some synthetic trace data (e.g., packet sizes over time)
    # Trace B is slightly shifted and noisy version of Trace A
    trace_a = [50, 1500, 1500, 40, 40, 1500, 50, 50]
    trace_b = [0, 50, 1500, 1500, 40, 50, 1500, 60] 
    
    timings_a = [0.1, 0.2, 0.25, 0.4, 0.45, 0.6, 0.7, 0.72]
    timings_b = [0.05, 0.12, 0.22, 0.27, 0.41, 0.48, 0.61, 0.75]

    print("--- Traffic Correlation Engine Analysis ---")
    print(f"Trace A: {trace_a}")
    print(f"Trace B: {trace_b}\n")
    
    results = engine.analyze(trace_a, trace_b, timings_a, timings_b)
    
    print(f"Pearson similarity:       {results['Pearson']:.2f}")
    print(f"Spearman similarity:      {results['Spearman']:.2f}")
    print(f"Cross-correlation:        {results['CrossCorrelation']:.2f}")
    print(f"Timing similarity:        {results['TimingSimilarity']:.2f}")
    print(f"Volume similarity:        {results['VolumeSimilarity']:.2f}")
    print(f"DTW similarity (V2):      {results['DTW']:.2f}")
    print(f"----------------------------------------")
    print(f"Overall Correlation Score: {results['OverallCorrelationScore']:.2f}")
