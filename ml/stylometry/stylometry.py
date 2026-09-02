import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import warnings

# Suppress warnings for clean execution
warnings.filterwarnings('ignore')

class StylometricFeatureExtractor:
    """Extracts Lexical, Character, and Syntactic features from text."""
    
    @staticmethod
    def extract_lexical(text):
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return [0, 0, 0]
            
        unique_words = set(words)
        vocab_richness = len(unique_words) / len(words)
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        # Simplified rare-word approximation (words > 8 chars)
        rare_words = len([w for w in words if len(w) > 8]) / len(words)
        
        return [vocab_richness, avg_word_length, rare_words]
        
    @staticmethod
    def extract_character(text):
        if not text:
            return [0, 0, 0]
            
        punct_count = len(re.findall(r'[^\w\s]', text)) / len(text)
        cap_count = len(re.findall(r'[A-Z]', text)) / len(text)
        # Simplified character n-gram representation (ratio of common bigrams like 'th', 'he')
        th_count = text.lower().count('th') / len(text)
        
        return [punct_count, cap_count, th_count]
        
    @staticmethod
    def extract_syntactic(text):
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return [0]
            
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        # Deep POS distributions require spaCy/NLTK. Simplified here to avoid heavy model loading in Phase 8 prototype.
        # Can easily integrate `spacy.load("en_core_web_sm")` for POS tags (Nouns, Verbs ratios) later.
        
        return [avg_sentence_length]

    @classmethod
    def get_all_features(cls, text):
        return (
            cls.extract_lexical(text) + 
            cls.extract_character(text) + 
            cls.extract_syntactic(text)
        )


class StylometryEngine:
    """
    PHASE 8: Stylometry / NLP Engine
    Extracts linguistic profiles and calculates style similarity.
    CRITICAL RULE: Stylometry provides SUPPORTING WEIGHT ONLY. It cannot confirm identity.
    """
    
    def __init__(self):
        # 1. TF-IDF + SVM Setup
        self.tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), max_features=1000)
        self.svm_classifier = SVC(kernel='linear', probability=True)
        self.is_svm_trained = False
        
        # 2. Semantic Setup (Sentence Transformer)
        # Using a lightweight model for speed in the hackathon prototype
        print("Loading Sentence Transformer model (this may take a moment on first run)...")
        try:
            self.transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_transformer = True
        except Exception as e:
            print(f"Failed to load SentenceTransformer: {e}. Falling back to TF-IDF only.")
            self.use_transformer = False

    def build_linguistic_profile(self, text):
        """Builds the comprehensive profile for a given text snippet."""
        profile = {
            "stylometric_features": StylometricFeatureExtractor.get_all_features(text),
            "tfidf_features": None, # Requires corpus fit, handled in batch
            "semantic_embedding": None
        }
        
        if self.use_transformer:
            profile["semantic_embedding"] = self.transformer.encode([text])[0]
            
        return profile

    def calculate_similarity(self, text_a, text_b):
        """
        Calculates similarity between two texts.
        Returns a support confidence score, explicitly marked as 'Supporting Evidence'.
        """
        prof_a = self.build_linguistic_profile(text_a)
        prof_b = self.build_linguistic_profile(text_b)
        
        scores = {}
        
        # 1. Stylometric Feature Euclidean Similarity
        f_a = np.array(prof_a["stylometric_features"])
        f_b = np.array(prof_b["stylometric_features"])
        dist = np.linalg.norm(f_a - f_b)
        scores["stylometric"] = max(0, 1 - (dist / 10)) # Arbitrary scaling for prototype
        
        # 2. Semantic Similarity (Cosine)
        if self.use_transformer:
            emb_a = prof_a["semantic_embedding"].reshape(1, -1)
            emb_b = prof_b["semantic_embedding"].reshape(1, -1)
            cos_sim = cosine_similarity(emb_a, emb_b)[0][0]
            scores["semantic"] = cos_sim
            
        # Combine into a final "supporting" weight (Semantic carries more weight if available)
        if "semantic" in scores:
            final_score = (scores["stylometric"] * 0.3) + (scores["semantic"] * 0.7)
        else:
            final_score = scores["stylometric"]
            
        return {
            "similarity_score": final_score,
            "interpretation": "Strong stylistic alignment." if final_score > 0.75 else "Weak/Moderate stylistic alignment.",
            "operational_rule": "STYLE SUPPORTS HYPOTHESIS ONLY. DO NOT USE AS SOLE ATTRIBUTION."
        }


if __name__ == "__main__":
    print("--- PHASE 8: Stylometry Engine Initialization ---")
    engine = StylometryEngine()
    
    # Example Texts
    text_target = "Hey guys, the server is down again. I'm going to reboot it in 5 mins. Don't push any updates until I say so. Thx!"
    text_suspect = "Server is down again. Going to reboot it in 5 mins. Do not push updates until I say so. Thx!"
    text_unrelated = "Hello everyone. The weekly meeting has been moved to Thursday at 2 PM. Please update your calendars accordingly."
    
    print("\n[Analyzing Target vs Suspect]")
    result_match = engine.calculate_similarity(text_target, text_suspect)
    print(f"Similarity Score: {result_match['similarity_score']:.2%}")
    print(f"Interpretation:   {result_match['interpretation']}")
    print(f"SYSTEM RULE:      {result_match['operational_rule']}")
    
    print("\n[Analyzing Target vs Unrelated]")
    result_diff = engine.calculate_similarity(text_target, text_unrelated)
    print(f"Similarity Score: {result_diff['similarity_score']:.2%}")
    print(f"Interpretation:   {result_diff['interpretation']}")
