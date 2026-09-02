import networkx as nx
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
import os

class MetadataExtractor:
    """Extracts metadata from various file types to identify OpSec failures."""
    
    @staticmethod
    def extract_image_metadata(file_path):
        """Extracts EXIF and basic properties from an image."""
        metadata = {}
        try:
            image = Image.open(file_path)
            metadata['format'] = image.format
            metadata['mode'] = image.mode
            metadata['size'] = image.size
            
            # Extract EXIF data
            exifdata = image.getexif()
            if exifdata:
                metadata['exif'] = {}
                for tag_id in exifdata:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exifdata.get(tag_id)
                    # Handle bytes which are common in EXIF UserComment
                    if isinstance(data, bytes):
                        data = data.decode('utf-8', errors='ignore')
                    metadata['exif'][tag] = data
        except Exception as e:
            metadata['error'] = str(e)
            
        return metadata

    @staticmethod
    def extract_document_metadata(file_path):
        """Mock extraction for document properties (PDF/DOCX)."""
        # In a full implementation, PyPDF2 or python-docx would be used here.
        return {
            'author': 'User_Desktop_1',
            'creation_date': '2023-10-27T10:00:00Z',
            'software': 'Microsoft Office Word',
            'company': 'Default Company'
        }


class InfrastructureGraph:
    """
    PHASE 10: Infrastructure + Metadata Intelligence
    Builds relationship graphs between Personas, Infrastructure, and Metadata 
    to track OpSec failures (not cryptography breaks).
    """
    def __init__(self):
        self.graph = nx.Graph()

    def add_persona_link(self, persona, entity_type, entity_value):
        """Links a persona to identifiers (Username, PGP, Domain, Wallet, Email)."""
        self.graph.add_node(persona, type='Persona')
        self.graph.add_node(entity_value, type=entity_type)
        self.graph.add_edge(persona, entity_value, relation='owns/uses')

    def add_infrastructure_link(self, source_entity, target_entity, source_type, target_type, relation):
        """Links infrastructure (Domain -> Cert -> Server -> IP)."""
        self.graph.add_node(source_entity, type=source_type)
        self.graph.add_node(target_entity, type=target_type)
        self.graph.add_edge(source_entity, target_entity, relation=relation)
        
    def add_metadata(self, entity_value, metadata_dict):
        """Attaches extracted metadata directly to a node."""
        if self.graph.has_node(entity_value):
            for k, v in metadata_dict.items():
                self.graph.nodes[entity_value][k] = v

    def find_opsec_failures(self, persona):
        """
        Traverses the graph from a Persona to find OpSec leaks.
        Example: Persona -> Domain -> Cert -> IP -> Hosting (Clear-net exposure).
        Example: Persona -> Image -> EXIF (GPS Data).
        """
        if not self.graph.has_node(persona):
            return []
            
        failures = []
        # Breadth-first search up to 4 degrees of separation
        edges = nx.bfs_edges(self.graph, source=persona, depth_limit=4)
        nodes = [persona] + [v for u, v in edges]
        
        for node in nodes:
            node_data = self.graph.nodes[node]
            node_type = node_data.get('type', 'Unknown')
            
            # Check for Clearnet IP exposure
            if node_type == 'IP' and not node.startswith('127.'):
                # Trace path back to persona to explain the leak
                path = nx.shortest_path(self.graph, source=persona, target=node)
                failures.append({
                    'type': 'Clearnet Infrastructure Exposure',
                    'entity': node,
                    'path': " -> ".join(path),
                    'description': 'Target infrastructure is exposed on the clearnet.'
                })
                
            # Check for Metadata Leaks (e.g., Software, Author, GPS)
            if node_type == 'Document' or node_type == 'Image':
                if 'author' in node_data and node_data['author'] != 'Unknown':
                    failures.append({
                        'type': 'Document Metadata Leak',
                        'entity': node,
                        'leak': f"Author: {node_data['author']}",
                        'description': 'Document contains identifying author tag.'
                    })
                if 'exif' in node_data and 'GPSInfo' in node_data['exif']:
                    failures.append({
                        'type': 'EXIF Location Leak',
                        'entity': node,
                        'leak': 'GPS Coordinates Found',
                        'description': 'Image contains raw GPS data.'
                    })
                    
        return failures

if __name__ == "__main__":
    print("--- PHASE 10: Infrastructure + Metadata Intelligence ---")
    engine = InfrastructureGraph()
    
    # 1. Build Persona Relationships
    persona = "ThreatActor_Omega"
    engine.add_persona_link(persona, "Username", "omega_admin")
    engine.add_persona_link(persona, "PGP", "0xABCD1234")
    engine.add_persona_link(persona, "Wallet", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
    engine.add_persona_link(persona, "Domain", "omega-dark-market.onion")
    engine.add_persona_link(persona, "Image", "proof_of_life.jpg")
    
    # 2. Build Infrastructure Relationships
    # (Mistake: The actor reused a cert from an old clearnet project for their hidden service)
    engine.add_infrastructure_link("omega-dark-market.onion", "Cert_SHA256_XYZ", "Domain", "Certificate", "uses")
    engine.add_infrastructure_link("Cert_SHA256_XYZ", "198.51.100.42", "Certificate", "IP", "hosted_on")
    engine.add_infrastructure_link("198.51.100.42", "DigitalOcean", "IP", "Hosting", "provisioned_by")
    
    # 3. Add Extracted Metadata (Simulated)
    # The actor uploaded an image without scrubbing EXIF
    simulated_exif = {
        'Make': 'Apple', 
        'Model': 'iPhone 13 Pro', 
        'DateTimeOriginal': '2023-11-05 14:32:01',
        'GPSInfo': {1: 'N', 2: (40.0, 42.0, 51.0), 3: 'W', 4: (74.0, 0.0, 21.0)} # Mock GPS
    }
    engine.add_metadata("proof_of_life.jpg", {'exif': simulated_exif})
    
    # 4. Analyze for OpSec Failures
    print(f"\nAnalyzing graph for OpSec failures linked to: {persona}...")
    failures = engine.find_opsec_failures(persona)
    
    if failures:
        print(f"\n[!] Detected {len(failures)} Operational Security Failures:\n")
        for f in failures:
            print(f"[{f['type']}]")
            print(f"  Entity : {f['entity']}")
            if 'path' in f:
                print(f"  Path   : {f['path']}")
            if 'leak' in f:
                print(f"  Leak   : {f['leak']}")
            print(f"  Detail : {f['description']}\n")
    else:
        print("\n[+] No obvious OpSec failures detected in graph.")
