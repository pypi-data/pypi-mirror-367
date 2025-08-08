# src/minichain/output_parsers/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseOutputParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> Any:
        pass
    
    def invoke(self, input: str, **kwargs: Any) -> Any:
        return self.parse(input)