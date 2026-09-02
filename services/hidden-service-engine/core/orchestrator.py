import json
import sys
import os

# Ensure the parent directory is in the path to allow imports when run as script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanners.http_scanner import HttpScanner
from scanners.tls_scanner import TlsScanner
from correlator.clearnet_matcher import ClearnetMatcher
from pipeline.evidence_formatter import format_infrastructure_evidence

def scan_target(target_url: str):
    """
    Main orchestration flow for Phase 4.
    """
    print(f"[*] Starting scan for {target_url}...")
    
    # 1. Scanners
    http_scanner = HttpScanner(target_url)
    tls_scanner = TlsScanner(target_url)
    
    print("[-] Running HTTP Fingerprinting...")
    http_data = http_scanner.scan()
    
    print("[-] Extracting TLS Certificates...")
    tls_data = tls_scanner.scan()
    
    # 2. Correlator
    print("[-] Correlating indicators against Clearnet...")
    matcher = ClearnetMatcher()
    correlation = matcher.correlate(http_data, tls_data)
    
    # 3. Format Evidence
    evidence = format_infrastructure_evidence(target_url, correlation)
    
    print("[+] Scan Complete. Generated Evidence:")
    print(json.dumps(evidence, indent=2))
    
    return evidence

if __name__ == "__main__":
    scan_target("http://mock-target-1.onion")
