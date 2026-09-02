from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    def __init__(self, source_id: str):
        self.source_id = source_id
        self.reliability = 1.0

    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from the source."""
        pass

    @abstractmethod
    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw data into standard format."""
        pass

    def run(self) -> List[Dict[str, Any]]:
        raw = self.fetch_data()
        return self.parse_data(raw)
