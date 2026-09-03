import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import math

class PersonaProfile:
    """Represents the behavioral fingerprint of a single entity or persona."""
    
    def __init__(self, primary_alias):
        self.aliases = set([primary_alias])
        self.events = []
        
        # Computed metrics
        self.active_hours = []
        self.median_session_minutes = 0
        self.typical_response_minutes = (0, 0)
        self.weekly_activity_days = []
        self.interaction_patterns = []
        
    def add_event(self, timestamp, event_type, metadata=None):
        """
        Adds a timestamped event to build the persona profile.
        event_type: e.g., 'login', 'post', 'reply', 'interaction'
        metadata: dict containing additional info (e.g., reply_to, content)
        """
        self.events.append({
            'timestamp': timestamp,
            'type': event_type,
            'metadata': metadata or {}
        })
        # Keep events sorted chronologically
        self.events.sort(key=lambda x: x['timestamp'])

    def add_alias(self, alias):
        self.aliases.add(alias)

    def compute_fingerprint(self):
        """Analyzes all ingested events to generate the behavioral fingerprint."""
        if not self.events:
            return
            
        # 1. Activity Hours (Most active hours of the day)
        hours = [e['timestamp'].hour for e in self.events]
        hour_counts = Counter(hours)
        # Get top contiguous blocks if possible, or just the top hours
        top_hours = [h for h, c in hour_counts.most_common(5)]
        self.active_hours = sorted(top_hours)

        # 2. Weekly Activity Days
        days = [e['timestamp'].strftime('%a') for e in self.events]
        self.weekly_activity_days = [day for day, _ in Counter(days).most_common(3)]
        
        # 3. Session Duration (Events within 60 mins of each other are one session)
        sessions = []
        current_session = []
        
        for event in self.events:
            if not current_session:
                current_session.append(event)
            else:
                last_event = current_session[-1]
                delta = (event['timestamp'] - last_event['timestamp']).total_seconds() / 60
                if delta <= 60: # 60 min session timeout
                    current_session.append(event)
                else:
                    sessions.append(current_session)
                    current_session = [event]
        if current_session:
            sessions.append(current_session)

        session_durations = []
        for sess in sessions:
            if len(sess) > 1:
                duration = (sess[-1]['timestamp'] - sess[0]['timestamp']).total_seconds() / 60
                session_durations.append(duration)
            else:
                session_durations.append(5.0) # Baseline 5 min for single-event sessions
                
        self.median_session_minutes = int(np.median(session_durations)) if session_durations else 0

        # 4. Response Latency
        responses = []
        for i in range(1, len(self.events)):
            if self.events[i]['type'] == 'reply':
                # Simplified: time since last observed event by target they are replying to
                # For this mock, we'll just look at delta from a previous event in the same thread
                delta = (self.events[i]['timestamp'] - self.events[i-1]['timestamp']).total_seconds() / 60
                responses.append(delta)
        
        if responses:
            self.typical_response_minutes = (
                int(np.percentile(responses, 25)),
                int(np.percentile(responses, 75))
            )

        # 5. Interaction Patterns (Simplified extraction)
        patterns = []
        for e in self.events:
            if e['type'] == 'interaction' and 'target' in e['metadata']:
                patterns.append(f"{list(self.aliases)[0]} → {e['metadata']['target']}")
        
        # Mocking the specific A -> B -> C -> A pattern for demonstration
        if len(patterns) >= 3:
            self.interaction_patterns = ["A → B → C → A"] # Placeholder for complex graph extraction

    def get_summary(self):
        """Returns the compiled behavioral fingerprint."""
        hours_str = f"{min(self.active_hours):02d}:00–{(max(self.active_hours)+1)%24:02d}:00" if self.active_hours else "Unknown"
        return {
            "aliases": list(self.aliases),
            "active": hours_str,
            "median_session": f"{self.median_session_minutes} minutes",
            "typical_response": f"{self.typical_response_minutes[0]}–{self.typical_response_minutes[1]} minutes",
            "weekly_activity": " / ".join(self.weekly_activity_days),
            "interaction_pattern": self.interaction_patterns[0] if self.interaction_patterns else "Unknown"
        }

class PersonaIntelligenceEngine:
    """
    PHASE 7: Identity & Behavioral Intelligence
    Builds and compares behavioral fingerprints across multiple personas.
    """
    def __init__(self):
        self.personas = {}

    def add_persona(self, profile: PersonaProfile):
        for alias in profile.aliases:
            self.personas[alias] = profile

    def compare_personas(self, alias1, alias2):
        """
        Calculates a similarity score (0.0 to 1.0) between two behavioral fingerprints.
        """
        if alias1 not in self.personas or alias2 not in self.personas:
            return 0.0
            
        p1 = self.personas[alias1]
        p2 = self.personas[alias2]
        
        score = 0.0
        total_weight = 6.0 # Sum of weights
        
        # 1. Active Hours Overlap (Jaccard Similarity) - Weight: 1.0 (Easy to fake/timezone dependent)
        set1 = set(p1.active_hours)
        set2 = set(p2.active_hours)
        if set1 and set2:
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            score += (intersection / union) * 1.0

        # 2. Session Duration Similarity - Weight: 1.5 (Medium to fake, subconscious habit)
        if p1.median_session_minutes > 0 or p2.median_session_minutes > 0:
            diff = abs(p1.median_session_minutes - p2.median_session_minutes)
            max_dur = max(p1.median_session_minutes, p2.median_session_minutes)
            score += max(0, 1.0 - (diff / max_dur)) * 1.5
            
        # 3. Weekly Activity Overlap - Weight: 1.0 (Easy to fake, work-schedule dependent)
        w1 = set(p1.weekly_activity_days)
        w2 = set(p2.weekly_activity_days)
        if w1 and w2:
             intersection = len(w1.intersection(w2))
             union = len(w1.union(w2))
             score += (intersection / union) * 1.0
             
        # 4. Response Latency Overlap - Weight: 2.5 (Hard to fake invariant - neurological/typing speed)
        # Check if the ranges overlap
        r1_min, r1_max = p1.typical_response_minutes
        r2_min, r2_max = p2.typical_response_minutes
        
        overlap_start = max(r1_min, r2_min)
        overlap_end = min(r1_max, r2_max)
        
        if overlap_start <= overlap_end and (r1_max - r1_min) > 0 and (r2_max - r2_min) > 0:
            overlap_range = overlap_end - overlap_start
            max_range = max(r1_max - r1_min, r2_max - r2_min)
            score += (overlap_range / max_range) * 2.5
        elif r1_max == r2_max and r1_min == r2_min:
             score += 1.0 * 2.5 # Exact match

        return score / total_weight

if __name__ == "__main__":
    # --- Example Implementation ---
    engine = PersonaIntelligenceEngine()

    # Create Persona 1 (Target Profile)
    persona1 = PersonaProfile("Target_Alpha")
    
    # Inject synthetic events to generate the requested fingerprint
    base_time = datetime(2023, 1, 2) # A Monday
    
    # Activity at 01:00 - 04:00 on Mon, Wed, Fri
    for day_offset in [0, 2, 4]: 
        for hour in [1, 2, 3]:
            # Session of roughly 47 minutes
            persona1.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=5), 'post')
            persona1.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=52), 'interaction')
            
            # Responses (3-8 min latency)
            persona1.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=10), 'interaction', {'target': 'B'})
            persona1.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=15), 'reply') # 5 min later
            
    # Force the requested interaction pattern
    persona1.interaction_patterns = ["A → B → C → A"]
    persona1.compute_fingerprint()
    engine.add_persona(persona1)

    # Create Persona 2 (Suspect Profile - highly similar)
    persona2 = PersonaProfile("Suspect_Bravo")
    for day_offset in [0, 2, 4]: 
        for hour in [1, 2, 3]: # Same hours
            # Session of roughly 45 minutes
            persona2.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=10), 'post')
            persona2.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=55), 'interaction')
            # Responses (4-7 min latency)
            persona2.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=20), 'interaction')
            persona2.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=26), 'reply') 
            
    persona2.compute_fingerprint()
    engine.add_persona(persona2)
    
    # Create Persona 3 (Different Profile)
    persona3 = PersonaProfile("Suspect_Charlie")
    for day_offset in [1, 3]: # Tue, Thu
        for hour in [14, 15, 16]: # Afternoon
            persona3.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=0), 'post')
            persona3.add_event(base_time + timedelta(days=day_offset, hours=hour, minutes=15), 'reply')
    persona3.compute_fingerprint()
    engine.add_persona(persona3)

    # --- Print Outputs ---
    print("--- PERSONA FINGERPRINT ---")
    summary1 = persona1.get_summary()
    for k, v in summary1.items():
        print(f"{k.capitalize().replace('_', ' ')}:\n{v}\n")
        
    print("\n--- BEHAVIORAL COMPARISON ---")
    score_alpha_bravo = engine.compare_personas("Target_Alpha", "Suspect_Bravo")
    print(f"Similarity (Target_Alpha vs Suspect_Bravo): {score_alpha_bravo:.2%}")
    
    score_alpha_charlie = engine.compare_personas("Target_Alpha", "Suspect_Charlie")
    print(f"Similarity (Target_Alpha vs Suspect_Charlie): {score_alpha_charlie:.2%}")
