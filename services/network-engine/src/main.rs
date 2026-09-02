mod parser;
mod analyzer;
mod sink;

use std::env;

fn main() {
    println!("[*] Starting PRISM Network Telemetry Engine (Rust)");
    
    // 1. Read mock flow data
    let filepath = env::args().nth(1).unwrap_or_else(|| "../../data/synthetic/mock_flows.json".to_string());
    println!("[-] Loading packet flows from: {}", filepath);
    
    let flows = match parser::parse_mock_flows(&filepath) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("[!] Failed to parse flows: {}", e);
            return;
        }
    };
    
    println!("[-] Parsed {} flows.", flows.len());
    
    // 2. Correlate
    println!("[-] Running traffic correlation analysis...");
    let correlations = analyzer::correlate_flows(&flows);
    
    println!("[+] Found {} potential flow correlations.", correlations.len());
    for corr in &correlations {
        println!("    -> Match: {} <-> {} (Confidence: {:.2})", corr.ingress_flow_id, corr.egress_flow_id, corr.confidence_score);
    }
    
    // 3. Sink to Redis (Mocked connection string for MVP if not provided)
    let redis_url = env::var("REDIS_URL").unwrap_or_else(|_| "redis://127.0.0.1:6379/0".to_string());
    println!("[-] Pushing results to Redis broker at {}...", redis_url);
    
    match sink::push_to_redis(&redis_url, &correlations) {
        Ok(_) => println!("[+] Successfully pushed to Redis."),
        Err(e) => eprintln!("[!] Redis push failed (Ensure Redis is running): {}", e),
    }
}
