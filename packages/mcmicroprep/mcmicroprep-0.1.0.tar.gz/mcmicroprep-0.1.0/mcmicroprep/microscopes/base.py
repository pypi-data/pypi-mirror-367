from abc import ABC, abstractmethod
from pathlib import Path

class MicroscopeHandler(ABC):
    """
    Base class for microscope-specific handlers.
    """
    name: str  # e.g. 'olympus'

    @abstractmethod
    def restructure_raw(self, image_root: Path):
        """Reorganize raw files into raw/ and misc_files/ in place."""
        pass

    @abstractmethod
    def params_template(self) -> dict:
        """(Optional) Return dict for param overrides; not used for file-based params."""
        pass
