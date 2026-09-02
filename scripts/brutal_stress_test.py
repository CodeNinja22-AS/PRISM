import sys
import os
import time

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(base_dir, 'services', 'ml-engine'))

from fusion import EvidenceFusionEngine

def run_stress_test():
    print("--- STARTING BRUTAL STRESS TEST ---")
    engine = EvidenceFusionEngine()
    
    # Generate 10,000 weak positive signals
    for i in range(10000):
        engine.add_evidence(f"Weak Signal {i}", 0.51, group=f"Group_{i%50}", reliability=0.5)
        
    # Generate 10,000 strong negative signals
    for i in range(10000):
        engine.add_evidence(f"Alibi {i}", 0.1, group=f"NegativeGroup_{i%10}", reliability=1.0)
        
    # Generate 1 extremely unreliable 100% confirmation (reliability=0.0)
    engine.add_evidence("Hacked DB Dump", 1.0, group="Compromised", reliability=0.0)
    
    print(f"Loaded {len(engine.evidence_pool)} pieces of synthetic evidence.")
    
    start_time = time.time()
    try:
        final_prob, independent_scores = engine.calculate_hybrid_bayesian_probability(prior=0.1)
        end_time = time.time()
        
        print(f"Fusion calculated in {end_time - start_time:.4f} seconds.")
        print(f"Final Probability: {final_prob}")
        
        # In current flawed logic, reliability=0.0 makes score 0.0 -> log odds is massively negative -> prob is 0.0
        if final_prob < 0.01:
            print("[VULNERABILITY FOUND]: Mathematical collapse due to reliability=0.0 clamping. Unreliable evidence acted as a definitive alibi.")
            
    except Exception as e:
        print(f"[FATAL CRASH]: {e}")

if __name__ == "__main__":
    run_stress_test()
