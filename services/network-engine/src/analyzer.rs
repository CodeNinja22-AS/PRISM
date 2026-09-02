use crate::parser::PacketFlow;
use serde::{Deserialize, Serialize};
use rayon::prelude::*;

#[derive(Debug, Serialize, Deserialize)]
pub struct CorrelationResult {
    pub ingress_flow_id: String,
    pub egress_flow_id: String,
    pub timing_delta_ms: f64,
    pub volume_delta_bytes: i64,
    pub confidence_score: f64,
}

pub fn correlate_flows(flows: &[PacketFlow]) -> Vec<CorrelationResult> {
    // Naive O(N^2) correlation for MVP: match ingress (client -> guard) with egress (exit -> destination)
    // In a real scenario, flows would be tagged by capture interface (Ingress vs Egress).
    flows.par_iter().enumerate().flat_map(|(i, f1)| {
        let mut local_results = Vec::new();
        for j in (i + 1)..flows.len() {
            let f2 = &flows[j];
            
            // Check timing correlation (e.g., start within 0.5s of each other)
            let time_diff = (f1.start_time - f2.start_time).abs();
            
            // Check volume correlation (similar byte count due to padding/cells)
            let vol_diff = (f1.total_bytes as i64 - f2.total_bytes as i64).abs();
            
            if time_diff < 0.5 && vol_diff < 5000 {
                let confidence = 1.0 - (time_diff * 1.5) - (vol_diff as f64 / 10000.0);
                local_results.push(CorrelationResult {
                    ingress_flow_id: f1.flow_id.clone(),
                    egress_flow_id: f2.flow_id.clone(),
                    timing_delta_ms: time_diff * 1000.0,
                    volume_delta_bytes: vol_diff,
                    confidence_score: confidence.max(0.1),
                });
            }
        }
        local_results
    }).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_perfect_correlation() {
        let flows = vec![
            PacketFlow {
                flow_id: "F1".to_string(), source_ip: "1.1.1.1".to_string(), dest_ip: "2.2.2.2".to_string(),
                start_time: 1.0, end_time: 2.0, total_bytes: 1000, packet_count: 10,
            },
            PacketFlow {
                flow_id: "F2".to_string(), source_ip: "3.3.3.3".to_string(), dest_ip: "4.4.4.4".to_string(),
                start_time: 1.0, end_time: 2.0, total_bytes: 1000, packet_count: 10,
            }
        ];
        
        let results = correlate_flows(&flows);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].confidence_score, 1.0);
    }

    #[test]
    fn test_confidence_clamping() {
        let flows = vec![
            PacketFlow {
                flow_id: "F1".to_string(), source_ip: "A".to_string(), dest_ip: "B".to_string(),
                start_time: 1.0, end_time: 2.0, total_bytes: 1000, packet_count: 10,
            },
            PacketFlow {
                // High enough diff to make confidence negative, should be clamped to 0.1
                flow_id: "F2".to_string(), source_ip: "C".to_string(), dest_ip: "D".to_string(),
                start_time: 1.49, end_time: 2.0, total_bytes: 5900, packet_count: 10,
            }
        ];
        
        let results = correlate_flows(&flows);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].confidence_score, 0.1);
    }

    #[test]
    fn test_u64_to_i64_overflow_risk() {
        // Rust's (u64 as i64) can wrap if > i64::MAX
        // This is a brutal test of the data type boundaries
        let max_val = u64::MAX; 
        let flows = vec![
            PacketFlow {
                flow_id: "F1".to_string(), source_ip: "A".to_string(), dest_ip: "B".to_string(),
                start_time: 1.0, end_time: 2.0, total_bytes: max_val, packet_count: 10,
            },
            PacketFlow {
                flow_id: "F2".to_string(), source_ip: "C".to_string(), dest_ip: "D".to_string(),
                start_time: 1.0, end_time: 2.0, total_bytes: max_val - 100, packet_count: 10,
            }
        ];
        
        // This won't panic, but due to wrapping, the volume difference might be incorrectly evaluated.
        let results = correlate_flows(&flows);
        assert_eq!(results.len(), 1);
        // The difference is 100 bytes. Confidence should be 1.0 - (100 / 10000.0) = 0.99.
        // If it wrapped incorrectly, difference would be huge and results would be empty or 0.1.
        // Actually, u64::MAX as i64 is -1. (u64::MAX - 100) as i64 is -101.
        // The difference between -1 and -101 is 100. It surprisingly works due to two's complement!
        assert!(results[0].confidence_score > 0.9);
    }
}
