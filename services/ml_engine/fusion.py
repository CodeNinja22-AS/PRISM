class CalibrationEngine:
    """
    Calibrates raw probabilities to ensure they reflect true accuracy.
    Uses Platt Scaling (Logistic Regression) to map scores to expected true probabilities.
    """
    def __init__(self):
        # Mock parameters for Platt scaling: P(y=1|x) = 1 / (1 + exp(A*f(x) + B))
        self.A = -0.8
        self.B = 0.2
        
    def calibrate(self, raw_probability):
        """Applies calibration to the raw probability."""
        if raw_probability <= 0.001 or raw_probability >= 0.999:
            return raw_probability
            
        import math
        # Transform back to log odds
        f_x = math.log(raw_probability / (1 - raw_probability)) 
        # Apply scaling
        calibrated_prob = 1 / (1 + math.exp(self.A * f_x + self.B))
        return calibrated_prob

class EvidenceItem:
    """Represents a single piece of evidence contributing to deanonymization."""
    def __init__(self, name, score, independence_group, reliability=1.0):
        self.name = name
        self.score = score  # Probability (0.0 to 1.0)
        self.independence_group = independence_group
        self.reliability = reliability  # Weight based on source trust/manipulation risk
        
    def get_weighted_score(self):
        """Applies reliability penalty/weight to the raw score."""
        # Bayesian non-linear scaling: pulls score to neutral prior (0.5) when reliability is 0.0
        return self.score * self.reliability + 0.5 * (1.0 - self.reliability)

class EvidenceFusionEngine:
    """
    PHASE 12: Evidence Fusion Engine
    Combines Network, Behavior, Stylometry, Blockchain, Infrastructure, 
    and Identity evidence into a final probability assessment, 
    preventing artificial confidence inflation through Independence Groups.
    """
    
    def __init__(self):
        self.evidence_pool = []
        self.calibrator = CalibrationEngine()
        
    def add_evidence(self, name, score, group, reliability=1.0):
        self.evidence_pool.append(EvidenceItem(name, score, group, reliability))

    def add_ensemble_evidence(self, name, model_scores, weights=None, group="Network", reliability=1.0):
        """
        Combines predictions from multiple ML models (e.g., Random Forest + DTW)
        into a single ensemble score before adding to the evidence pool.
        """
        if not weights:
            weights = [1.0 / len(model_scores)] * len(model_scores)
            
        ensemble_score = sum(s * w for s, w in zip(model_scores, weights))
        self.add_evidence(f"{name} (Ensemble)", ensemble_score, group, reliability)

    def _group_evidence(self):
        """Groups dependent evidence to prevent confidence inflation."""
        groups = {}
        for ev in self.evidence_pool:
            if ev.independence_group not in groups:
                groups[ev.independence_group] = []
            groups[ev.independence_group].append(ev)
        return groups

    def _reduce_dependent_evidence(self, group_items):
        """
        Reduces multiple dependent clues (e.g., Profile Name & Email) 
        into a single representative probability for that group.
        Instead of averaging (which dampens strong signals), we use a logical OR 
        approximation or simply take the max reliable signal for safety.
        """
        if not group_items:
            return 0.5 # Neutral prior
            
        # For this prototype, we take the maximum weighted score within the dependent group
        # This prevents 5 weak username links from mathematically overwhelming 1 strong network link.
        max_score = max(item.get_weighted_score() for item in group_items)
        return max_score

    def calculate_hybrid_bayesian_probability(self, prior=0.1):
        """
        Applies a modified Bayesian updating formula to the independent evidence groups.
        Conceptually: P(H|E) = (P(E|H) * P(H)) / P(E)
        We use log-odds (logit) transformation for numerical stability when combining multiple independent signals.
        """
        if not self.evidence_pool:
            return prior, []
            
        groups = self._group_evidence()
        independent_scores = []
        
        for group_name, items in groups.items():
            reduced_score = self._reduce_dependent_evidence(items)
            independent_scores.append(reduced_score)
            
        # Convert Prior to Log-Odds
        # Prior is low (0.1) because out of all actors on the dark web, the chance these two are the same is initially small.
        log_odds_prior = self._to_log_odds(prior)
        
        total_log_evidence = 0
        for score in independent_scores:
            # We treat the score from the sub-engines as the likelihood ratio or posterior of that specific engine
            # Convert engine score to log-odds and add to total evidence
            # Clamp scores to avoid math domain errors
            clamped_score = max(0.001, min(0.999, score))
            total_log_evidence += self._to_log_odds(clamped_score)
            
        # Final Log-Odds = Prior Log-Odds + Sum of Evidence Log-Odds
        final_log_odds = log_odds_prior + total_log_evidence
        
        # Convert back to probability
        final_probability = self._to_probability(final_log_odds)
        
        # Apply calibration
        calibrated_probability = self.calibrator.calibrate(final_probability)
        
        return calibrated_probability, independent_scores

    def _to_log_odds(self, p):
        import math
        return math.log(p / (1 - p))
        
    def _to_probability(self, log_odds):
        import math
        return 1 / (1 + math.exp(-log_odds))


if __name__ == "__main__":
    print("--- PHASE 12: Evidence Fusion Engine ---")
    
    engine = EvidenceFusionEngine()
    
    # 1. Input Raw Evidence (Notice how Identity has 3 pieces of evidence)
    # Network
    engine.add_evidence("Traffic Timing Correlation", 0.92, group="Network", reliability=0.95)
    
    # Blockchain
    engine.add_evidence("Wallet Co-spending", 0.87, group="Blockchain", reliability=0.99)
    
    # Infrastructure
    engine.add_evidence("Shared Clearnet IP", 0.81, group="Infrastructure", reliability=0.90)
    
    # Behavior
    engine.add_evidence("Active Hours Overlap", 0.78, group="Behavior", reliability=0.85)
    
    # Stylometry (Supporting only - reliability modifier reduces its impact)
    engine.add_evidence("Linguistic Profile", 0.74, group="Stylometry", reliability=0.60) # Note the low reliability modifier
    
    # Identity (These are highly dependent - if you use the same username, you likely use the same email)
    engine.add_evidence("Username Match", 0.52, group="Identity", reliability=0.80)
    engine.add_evidence("Profile Name Match", 0.60, group="Identity", reliability=0.80)
    engine.add_evidence("Email Recovery Link", 0.55, group="Identity", reliability=0.80)

    # 2. Perform Fusion
    print("\nProcessing Independence Groups to prevent artificial confidence inflation...")
    final_prob, group_scores = engine.calculate_hybrid_bayesian_probability(prior=0.1)
    
    # 3. Output Explanation
    groups = engine._group_evidence()
    print("\n[Evidence Independence Reduction]")
    for group, items in groups.items():
        raw_scores = [f"{i.name}({i.score:.2f})" for i in items]
        reduced = engine._reduce_dependent_evidence(items)
        print(f"  {group.ljust(15)}: {len(items)} inputs -> Reduced Representative Score: {reduced:.2f} | Raw: {raw_scores}")

    print(f"\n[Final Bayesian Fusion]")
    print(f"  Prior Probability : 10.00% (Baseline assumption)")
    print(f"  Final Probability : {final_prob:.2%} (Same Underlying Actor)")
    print("\nExplanation: Graph inference explicitly prevented the 3 weak Identity matches from stacking and inflating the score, while combining independent high-confidence network and blockchain indicators to reach a definitive conclusion.")
