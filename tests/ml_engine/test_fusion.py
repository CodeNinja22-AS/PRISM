import pytest
import math
from services.ml_engine.fusion import EvidenceFusionEngine, EvidenceItem

def test_empty_fusion():
    engine = EvidenceFusionEngine()
    prob, scores = engine.calculate_hybrid_bayesian_probability(prior=0.1)
    assert prob == 0.1
    assert scores == []

def test_dependent_evidence_reduction():
    engine = EvidenceFusionEngine()
    engine.add_evidence("Id 1", 0.6, group="Identity")
    engine.add_evidence("Id 2", 0.8, group="Identity")
    engine.add_evidence("Id 3", 0.7, group="Identity")
    
    reduced = engine._reduce_dependent_evidence(engine._group_evidence()["Identity"])
    # The max score should be returned (0.8 * 1.0 = 0.8)
    assert reduced == 0.8

def test_extreme_contradictory_evidence():
    engine = EvidenceFusionEngine()
    # High confidence evidence
    for _ in range(50):
        engine.add_evidence("Network Match", 0.99, group="Network")
    # Strong negative evidence (low probability)
    for _ in range(50):
        engine.add_evidence("Alibi", 0.01, group="Alibi")
        
    prob, _ = engine.calculate_hybrid_bayesian_probability(prior=0.5)
    
    # Since they perfectly balance, and we take max within groups...
    # Wait, Network max is 0.99, Alibi max is 0.01.
    # Log odds of 0.99 + log odds of 0.01 + log odds of 0.5 (prior)
    # Log odds of 0.99 = log(99), Log odds of 0.01 = log(1/99) = -log(99)
    # They should cancel exactly to the prior!
    assert math.isclose(prob, 0.5, rel_tol=1e-3)

def test_zero_reliability_bug():
    engine = EvidenceFusionEngine()
    # If a source is highly unreliable, reliability = 0.0
    engine.add_evidence("Fake DB Leak", 0.99, group="Identity", reliability=0.0)
    
    prob, scores = engine.calculate_hybrid_bayesian_probability(prior=0.5)
    
    # In the fixed implementation, 0.0 reliability neutralizes the evidence to 0.5 (neutral)
    assert prob == 0.5

def test_prior_boundaries():
    engine = EvidenceFusionEngine()
    engine.add_evidence("Test", 0.9, group="Test")
    
    # Test prior = 0.0 or 1.0 (should cause ZeroDivisionError or ValueError in log)
    with pytest.raises((ZeroDivisionError, ValueError)):
        engine.calculate_hybrid_bayesian_probability(prior=1.0)
        
    with pytest.raises((ZeroDivisionError, ValueError)):
        engine.calculate_hybrid_bayesian_probability(prior=0.0)
