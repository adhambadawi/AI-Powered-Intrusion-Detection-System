from dataclasses import dataclass
from datetime import datetime
from src.data_models.flow import Flow

@dataclass
class Alert:
    timestamp: datetime
    attack_probability: float
    flow: Flow

    def to_csv(self) -> str:
        return [self.timestamp, self.attack_probability] + self.flow.to_csv()
