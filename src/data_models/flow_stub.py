from dataclasses import dataclass

@dataclass
class FlowStub:
    """Class for representing a dummy flow for the test stub"""
    row_index: int
    malicious: bool

    def __repr__(self):
        return f"Dummy {"malicious" if self.malicious else "benign"} flow #{self.row_index}"