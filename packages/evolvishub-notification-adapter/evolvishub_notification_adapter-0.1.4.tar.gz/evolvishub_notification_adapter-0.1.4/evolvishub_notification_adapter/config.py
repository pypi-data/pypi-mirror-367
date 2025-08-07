import os
import yaml
import configparser
from typing import Optional, Dict, Any
import logging

class Config:
    """Configuration manager for the notification adapter."""
    
    def __init__(self, config_path: str):
        """
        Initialize configuration manager.
        
        Args:
            config_path (str): Path to the configuration file (YAML or INI).
                This must be provided by the external application.
        
        Raises:
            ValueError: If config_path is not provided or file doesn't exist.
            FileNotFoundError: If the configuration file doesn't exist.
        """
        if not config_path:
            raise ValueError("Configuration file path must be provided")
            
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._setup_logging()
        self._load_config()

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('evolvishub_notification_adapter')

    def _load_config(self):
        """Load configuration from file."""
        if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
            self._load_yaml_config()
        elif self.config_path.endswith('.ini'):
            self._load_ini_config()
        else:
            raise ValueError(f"Unsupported config file format: {self.config_path}")

    def _load_yaml_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading YAML config: {e}")
            raise

    def _load_ini_config(self):
        """Load configuration from INI file."""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)
            
            # Convert INI to dictionary format
            self.config = {
                'database': {
                    'path': config.get('database', 'path'),
                    'directory': config.get('database', 'directory')
                },
                'logging': {
                    'enabled': config.getboolean('logging', 'enabled'),
                    'level': config.get('logging', 'level')
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading INI config: {e}")
            raise

    def get_database_path(self) -> str:
        """Get the database file path."""
        db_dir = self.config['database']['directory']
        db_file = self.config['database']['path']
        
        # Create directory if it doesn't exist
        os.makedirs(db_dir, exist_ok=True)
        
        return os.path.join(db_dir, db_file)

    def is_logging_enabled(self) -> bool:
        """Check if logging is enabled."""
        return self.config['logging']['enabled']

    def get_log_level(self) -> str:
        """Get the logging level."""
        return self.config['logging']['level'] 