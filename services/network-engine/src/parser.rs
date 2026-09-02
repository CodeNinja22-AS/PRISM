use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PacketFlow {
    pub flow_id: String,
    pub source_ip: String,
    pub dest_ip: String,
    pub start_time: f64,
    pub end_time: f64,
    pub total_bytes: u64,
    pub packet_count: u64,
}

pub fn parse_mock_flows(filepath: &str) -> Result<Vec<PacketFlow>, Box<dyn std::error::Error>> {
    let data = fs::read_to_string(filepath)?;
    let flows: Vec<PacketFlow> = serde_json::from_str(&data)?;
    Ok(flows)
}
