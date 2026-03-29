import logging
from utils.logger import get_logger


class TestLogger:
    """Test cases for logger utility."""

    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_same_name_returns_same_instance(self):
        """Test that calling get_logger with same name returns same instance."""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")

        assert logger1 is logger2

    def test_get_logger_different_names_different_instances(self):
        """Test that different names return different logger instances."""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name

    def test_logger_has_correct_level(self):
        """Test that logger is properly configured."""
        logger = get_logger("test_level")

        assert logger is not None
        assert logger.name == "test_level"

        root_logger = logging.getLogger()
        assert root_logger.level != logging.NOTSET