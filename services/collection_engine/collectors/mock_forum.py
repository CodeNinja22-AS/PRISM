import json
import os
from celery import shared_task
from collectors.base import BaseCollector
from pipeline.normalizer import normalize_forum_post
from pipeline.deduplicator import process_evidence

class MockForumCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_id="src_mock_forum_01")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.dataset_path = os.path.join(current_dir, "../../../data/synthetic/mock_forum_dataset.json")

    def fetch_data(self):
        if not os.path.exists(self.dataset_path):
            print(f"File not found: {self.dataset_path}")
            return []
        with open(self.dataset_path, "r") as f:
            return json.load(f)

    def parse_data(self, raw_data):
        return raw_data

@shared_task(name="collectors.mock_forum.run_mock_collection")
def run_mock_collection():
    collector = MockForumCollector()
    raw_posts = collector.run()
    
    processed_count = 0
    for post in raw_posts:
        normalized = normalize_forum_post(post, collector.source_id, collector.reliability)
        process_evidence(normalized)
        processed_count += 1
        
    return f"Processed {processed_count} posts from mock forum."
