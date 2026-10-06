import pytest
import sys
from unittest.mock import patch

def test_startup_fails_same_model():
    with patch("app.core.config.config.refiner") as mock_refiner:
        with patch("app.core.config.config.extractor") as mock_extractor:
            mock_refiner.provider = "gemini"
            mock_refiner.model = "gemini-test"
            mock_extractor.provider = "gemini"
            mock_extractor.model = "gemini-test"
            
            from app.main import startup_event
            import asyncio
            
            with pytest.raises(ValueError, match="Refiner and Extractor must use different models"):
                asyncio.run(startup_event())
