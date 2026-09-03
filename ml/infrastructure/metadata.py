import os
from datetime import datetime

try:
    import exifread
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class MetadataLeakEngine:
    """
    Analyzes intercepted files (e.g., images, PDFs) for accidental metadata leaks 
    that could deanonymize a user (GPS coordinates, author names, device models).
    """
    def __init__(self):
        self.extracted_data = []

    def analyze_image(self, file_path):
        """Extracts EXIF data from images."""
        if not EXIF_AVAILABLE:
            return {"mock": True, "warning": "exifread not installed. Returning mock data.",
                    "Device": "iPhone 13 Pro", "GPS": "37.7749,-122.4194"}
            
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                for tag in tags.keys():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                        metadata[tag] = str(tags[tag])
        except Exception as e:
            metadata["error"] = str(e)
            
        return metadata

    def analyze_pdf(self, file_path):
        """Extracts author and creation metadata from PDFs."""
        if not PDF_AVAILABLE:
            return {"mock": True, "warning": "PyPDF2 not installed. Returning mock data.",
                    "Author": "John Doe", "Creator": "Microsoft Word"}
            
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                info = reader.metadata
                if info:
                    for key, value in info.items():
                        metadata[key.strip('/')] = value
        except Exception as e:
            metadata["error"] = str(e)
            
        return metadata

    def process_file(self, file_path, source_persona):
        """Processes a file and assigns extracted metadata to a persona."""
        ext = os.path.splitext(file_path)[1].lower()
        
        extracted = {}
        if ext in ['.jpg', '.jpeg', '.tiff', '.png']:
            extracted = self.analyze_image(file_path)
        elif ext == '.pdf':
            extracted = self.analyze_pdf(file_path)
        else:
            extracted = {"info": "Unsupported file type for deep metadata analysis"}
            
        record = {
            "timestamp": datetime.now().isoformat(),
            "source_persona": source_persona,
            "file": file_path,
            "metadata": extracted
        }
        self.extracted_data.append(record)
        return record
        
    def cross_reference_personas(self):
        """
        Looks for metadata overlaps between different personas.
        e.g., Target A and Suspect B uploaded files created by 'John Doe'.
        """
        # Group metadata by values to find commonalities
        value_map = {}
        for record in self.extracted_data:
            persona = record["source_persona"]
            for key, val in record["metadata"].items():
                if key in ["error", "warning", "mock", "info"]: continue
                
                # Simple string normalization
                norm_val = str(val).lower().strip()
                if not norm_val: continue
                
                if norm_val not in value_map:
                    value_map[norm_val] = {"personas": set(), "keys": set()}
                    
                value_map[norm_val]["personas"].add(persona)
                value_map[norm_val]["keys"].add(key)
                
        # Find overlaps
        overlaps = []
        for val, data in value_map.items():
            if len(data["personas"]) > 1:
                overlaps.append({
                    "shared_value": val,
                    "metadata_keys": list(data["keys"]),
                    "personas_involved": list(data["personas"])
                })
                
        return overlaps


if __name__ == "__main__":
    print("--- PHASE X: Metadata Leak Analysis ---")
    
    engine = MetadataLeakEngine()
    
    print("\n[1] Processing Intercepted Files...")
    # Using mock file paths for demonstration
    r1 = engine.process_file("target_upload.jpg", source_persona="Target_X")
    print(f"  Target_X -> target_upload.jpg: {r1['metadata'].get('Device', 'Extracted')}")
    
    r2 = engine.process_file("suspect_resume.pdf", source_persona="Suspect_Y")
    print(f"  Suspect_Y -> suspect_resume.pdf: {r2['metadata'].get('Author', 'Extracted')}")
    
    # Inject an overlap for demonstration
    engine.extracted_data.append({
        "source_persona": "Suspect_Y", 
        "metadata": {"Device": "iPhone 13 Pro"}
    })
    
    print("\n[2] Cross-Referencing Personas for Metadata Overlaps...")
    overlaps = engine.cross_reference_personas()
    
    for overlap in overlaps:
        print(f"  [!] CRITICAL HIT: Shared Metadata Found!")
        print(f"      Value    : '{overlap['shared_value']}'")
        print(f"      Context  : {overlap['metadata_keys']}")
        print(f"      Personas : {overlap['personas_involved']}")
        
    if overlaps:
        print("\n  -> Action: This provides a high-confidence Identity link for the Fusion Engine.")
