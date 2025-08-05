"""Configuration and directory management for LitAI."""

import json
from pathlib import Path
from typing import Any

from structlog import get_logger

logger = get_logger()


class Config:
    """Manages LitAI configuration and directory structure."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize config with base directory.

        Args:
            base_dir: Base directory for LitAI data. Defaults to ~/.litai
        """
        if base_dir is None:
            base_dir = Path.home() / ".litai"
        self.base_dir = Path(base_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.base_dir,
            self.pdfs_dir,
            self.db_dir,
        ]

        for dir_path in directories:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info("Created directory", path=str(dir_path))

    @property
    def pdfs_dir(self) -> Path:
        """Directory for storing downloaded PDFs."""
        return self.base_dir / "pdfs"

    @property
    def db_dir(self) -> Path:
        """Directory for database files."""
        return self.base_dir / "db"

    @property
    def db_path(self) -> Path:
        """Path to the SQLite database file."""
        return self.db_dir / "litai.db"

    def pdf_path(self, paper_id: str) -> Path:
        """Get the path for a specific paper's PDF.

        Args:
            paper_id: Unique identifier for the paper

        Returns:
            Path where the PDF should be stored
        """
        return self.pdfs_dir / f"{paper_id}.pdf"
    
    @property
    def config_path(self) -> Path:
        """Path to the configuration file."""
        return self.base_dir / "config.json"
    
    def load_config(self) -> dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dict or empty dict if file doesn't exist
        """
        if not self.config_path.exists():
            return {}
        
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                logger.info("Loaded configuration", path=str(self.config_path))
                return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load config", path=str(self.config_path), error=str(e))
            return {}
    
    def save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info("Saved configuration", path=str(self.config_path))
        except IOError as e:
            logger.error("Failed to save config", path=str(self.config_path), error=str(e))
            raise
    
    def update_config(self, key_path: str, value: Any) -> None:
        """Update a specific configuration value.
        
        Args:
            key_path: Dot-separated path to config key (e.g., "llm.provider")
            value: Value to set
        """
        config = self.load_config()
        
        # Navigate through the key path, creating dicts as needed
        keys = key_path.split(".")
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
        
        self.save_config(config)
    
    def get_vi_mode(self) -> bool:
        """Get vi mode setting from configuration.
        
        Returns:
            True if vi mode is enabled, False otherwise (default)
        """
        config = self.load_config()
        return config.get("editor", {}).get("vi_mode", False)
