use crate::parser::PacketFlow;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct CorrelationResult {
    pub ingress_flow_id: String,
    pub egress_flow_id: String,
    pub timing_delta_ms: f64,
    pub volume_delta_bytes: i64,
    pub confidence_score: f64,
}

pub fn correlate_flows(flows: &[PacketFlow]) -> Vec<CorrelationResult> {
    let mut results = Vec::new();
    
    // Naive O(N^2) correlation for MVP: match ingress (client -> guard) with egress (exit -> destination)
    // In a real scenario, flows would be tagged by capture interface (Ingress vs Egress).
    for i in 0..flows.len() {
        for j in (i + 1)..flows.len() {
            let f1 = &flows[i];
            let f2 = &flows[j];
            
            // Check timing correlation (e.g., start within 0.5s of each other)
            let time_diff = (f1.start_time - f2.start_time).abs();
            
            // Check volume correlation (similar byte count due to padding/cells)
            let vol_diff = (f1.total_bytes as i64 - f2.total_bytes as i64).abs();
            
            if time_diff < 0.5 && vol_diff < 5000 {
                let confidence = 1.0 - (time_diff * 1.5) - (vol_diff as f64 / 10000.0);
                results.push(CorrelationResult {
                    ingress_flow_id: f1.flow_id.clone(),
                    egress_flow_id: f2.flow_id.clone(),
                    timing_delta_ms: time_diff * 1000.0,
                    volume_delta_bytes: vol_diff,
                    confidence_score: confidence.max(0.1),
                });
            }
        }
    }
    
    results
}
