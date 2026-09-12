from abc import ABC, abstractmethod
from typing import List


class ReconTool(ABC):
    """
    Base class for all recon tool adapters.
    Every adapter implements execute().
    """

    @abstractmethod
    def execute(self, target: str) -> List[dict]:
        """
        Run the tool against a target.
        Returns list of structured results.
        Never raises — returns empty list on failure.
        """
        pass

    def is_available(self) -> bool:
        """Check if the underlying tool is installed."""
        import shutil
        return shutil.which(self.binary_name) is not None