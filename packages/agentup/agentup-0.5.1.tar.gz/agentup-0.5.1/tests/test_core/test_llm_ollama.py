# Add src to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestOllamaProviderInitialization:
    """Test the LLMResponse data class."""
