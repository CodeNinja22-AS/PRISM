use redis::Commands;
use crate::analyzer::CorrelationResult;

pub fn push_to_redis(redis_url: &str, results: &[CorrelationResult]) -> Result<(), Box<dyn std::error::Error>> {
    let client = redis::Client::open(redis_url)?;
    let mut con = client.get_connection()?;
    
    for result in results {
        let payload = serde_json::to_string(result)?;
        let _: () = con.lpush("network_telemetry", payload)?;
    }
    
    Ok(())
}
