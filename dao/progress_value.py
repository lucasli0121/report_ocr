from dataclasses import dataclass

@dataclass
class ProgressValue:
    value: float = 0.0
    def __init__(self, value: float = 0.0):
        self.value = value
    def set_value(self, value: float):
        self.value = value