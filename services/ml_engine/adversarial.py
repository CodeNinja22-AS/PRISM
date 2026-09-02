import copy
from .fusion import EvidenceFusionEngine

class AdversarialEngine:
    """
    PHASE 13: Adversarial Analysis Engine
    Tries to disprove the attribution by performing leave-one-out analysis 
    and generating alternative hypotheses for evidence.
    """
    
    def __init__(self, base_fusion_engine: EvidenceFusionEngine):
        self.base_engine = base_fusion_engine
        
        # Library of alternative explanations (Devil's Advocate)
        self.alternative_hypotheses = {
            "Network": "Could traffic similarity be natural coincidence (e.g. streaming same video)?",
            "Blockchain": "Could the wallet relationship be indirect (e.g. common darknet market deposit wallet)?",
            "Infrastructure": "Could the infrastructure be a shared/bulletproof hosting provider?",
            "Stylometry": "Could the writing style be intentionally copied (e.g. using standard templates or LLMs)?",
            "Behavior": "Could the timing similarity occur naturally due to shared timezone constraints?",
            "Identity": "Could multiple people operate the same account (account sharing/compromise)?"
        }

    def _generate_adversarial_questions(self, groups):
        """Generates the questions meant to challenge the investigator."""
        questions = []
        for group in groups:
            if group in self.alternative_hypotheses:
                questions.append(self.alternative_hypotheses[group])
        return questions

    def run_leave_one_out_analysis(self, prior=0.1):
        """
        Removes each evidence family one by one to see how the overall 
        confidence holds up.
        """
        # Get baseline confidence
        base_confidence, _ = self.base_engine.calculate_hybrid_bayesian_probability(prior=prior)
        
        # Get distinct groups present
        groups = self.base_engine._group_evidence().keys()
        
        leave_one_out_results = {}
        max_drop = 0
        most_critical_group = None
        
        for group_to_remove in groups:
            # Create a temporary fusion engine without this group
            temp_engine = EvidenceFusionEngine()
            for ev in self.base_engine.evidence_pool:
                if ev.independence_group != group_to_remove:
                    temp_engine.add_evidence(ev.name, ev.score, ev.independence_group, ev.reliability)
            
            # Recalculate
            new_confidence, _ = temp_engine.calculate_hybrid_bayesian_probability(prior=prior)
            leave_one_out_results[group_to_remove] = new_confidence
            
            drop = base_confidence - new_confidence
            if drop > max_drop:
                max_drop = drop
                most_critical_group = group_to_remove
                
        return {
            "baseline": base_confidence,
            "leave_one_out": leave_one_out_results,
            "most_critical": most_critical_group,
            "max_drop": max_drop,
            "adversarial_questions": self._generate_adversarial_questions(groups)
        }

    def evaluate_robustness(self, analysis_results):
        """
        Calculates attribution robustness.
        Robustness is high if removing any single piece of evidence 
        doesn't crash the overall confidence.
        """
        base = analysis_results["baseline"]
        if base <= 0:
             return 0.0
             
        max_drop = analysis_results["max_drop"]
        
        # If the max drop destroys the confidence (e.g., from 94% to 10%), robustness is very low.
        # Simple formula: 1.0 - (max_drop / base)
        robustness = max(0.0, 1.0 - (max_drop / base))
        return robustness


if __name__ == "__main__":
    print("--- PHASE 13: Adversarial Analysis Engine ---")
    
    # 1. Setup the baseline engine (From Phase 12)
    fusion_engine = EvidenceFusionEngine()
    fusion_engine.add_evidence("Traffic Timing", 0.92, group="Network", reliability=0.95)
    fusion_engine.add_evidence("Wallet Co-spending", 0.87, group="Blockchain", reliability=0.99)
    fusion_engine.add_evidence("Shared Clearnet IP", 0.81, group="Infrastructure", reliability=0.90)
    fusion_engine.add_evidence("Active Hours Overlap", 0.78, group="Behavior", reliability=0.85)
    fusion_engine.add_evidence("Linguistic Profile", 0.74, group="Stylometry", reliability=0.60)
    
    # Intentionally leaving out Identity for this test to show reliance on Network/Blockchain
    
    # 2. Run Adversarial Engine
    adv_engine = AdversarialEngine(fusion_engine)
    results = adv_engine.run_leave_one_out_analysis(prior=0.1)
    robustness = adv_engine.evaluate_robustness(results)
    
    # 3. Output Research-Grade Report
    print(f"\n[Adversarial Challenge: Alternative Explanations]")
    for q in results["adversarial_questions"]:
        print(f"  ? {q}")
        
    print(f"\n[Leave-One-Out Analysis]")
    print(f"  Overall Confidence: {results['baseline']:.2%}")
    for group, score in results["leave_one_out"].items():
        print(f"    Without {group.ljust(15)} : {score:.2%}")
        
    print(f"\n[System Conclusion]")
    print(f"  Attribution confidence : {results['baseline']:.2%}")
    print(f"  Attribution robustness : {robustness:.2%}")
    print(f"\n  Note: Attribution is strongly dependent on [{results['most_critical']}] evidence.")
    print(f"  (Removing it causes a {results['max_drop']:.2%} drop in overall confidence).")
