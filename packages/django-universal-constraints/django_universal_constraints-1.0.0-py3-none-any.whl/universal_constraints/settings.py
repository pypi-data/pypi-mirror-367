"""
Settings management for universal constraints.

This module handles per-database configuration for the auto-discovery and validation system.
"""

from django.conf import settings
import logging

# Simplified default configuration per database
DEFAULT_SETTINGS = {
    'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
    'RACE_CONDITION_PROTECTION': True,
    'REMOVE_DB_CONSTRAINTS': True,
    'LOG_LEVEL': 'INFO',
}

logger = logging.getLogger('universal_constraints.settings')


class ConstraintSettings:
    """Configuration manager for universal constraints with per-database settings."""
    
    def __init__(self):
        self._db_settings = {}
        self._load_settings()
    
    def _load_settings(self):
        """Load per-database settings from Django settings."""
        user_settings = getattr(settings, 'UNIVERSAL_CONSTRAINTS', {})
        
        # Each key is a database alias with its settings
        for db_alias, db_config in user_settings.items():
            # Merge with defaults
            db_settings = DEFAULT_SETTINGS.copy()
            db_settings.update(db_config)
            
            # Validate settings for this database
            self._validate_database_settings(db_alias, db_settings)
            
            self._db_settings[db_alias] = db_settings
        
        # Configure logging (use first database's log level or default)
        self._configure_logging()
    
    def _validate_database_settings(self, db_alias, db_settings):
        """Validate configuration settings for a specific database."""
        log_level = db_settings.get('LOG_LEVEL', 'INFO')
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            raise ValueError(f"Invalid LOG_LEVEL for database '{db_alias}': {log_level}")
        
        # Validate boolean settings
        bool_settings = ['RACE_CONDITION_PROTECTION', 'REMOVE_DB_CONSTRAINTS']
        for setting in bool_settings:
            if setting in db_settings and not isinstance(db_settings[setting], bool):
                raise ValueError(f"Setting '{setting}' for database '{db_alias}' must be a boolean")
        
        # Validate EXCLUDE_APPS is a list
        exclude_apps = db_settings.get('EXCLUDE_APPS', [])
        if not isinstance(exclude_apps, list):
            raise ValueError(f"EXCLUDE_APPS for database '{db_alias}' must be a list")
        
        # Validate backend wrapper requirement
        self._validate_backend_wrapper_requirement(db_alias, db_settings)
    
    def _validate_backend_wrapper_requirement(self, db_alias, db_settings):
        """Validate that backend wrapper is used when REMOVE_DB_CONSTRAINTS is True."""
        if db_settings.get('REMOVE_DB_CONSTRAINTS', False):
            # Check if database is using our wrapper
            db_config = settings.DATABASES.get(db_alias, {})
            engine = db_config.get('ENGINE', '')
            if 'universal_constraints.backend' not in engine:
                logger.warning(
                    f"Database '{db_alias}' has REMOVE_DB_CONSTRAINTS=True but is not using "
                    f"the universal_constraints backend wrapper. Constraint removal may not "
                    f"work properly. Consider using 'universal_constraints.backend' "
                    f"as your ENGINE with WRAPPED_ENGINE pointing to your actual backend."
                )
    
    def _configure_logging(self):
        """Configure logging for the unique constraints system."""
        # Use the first database's log level, or default
        log_level_str = 'INFO'
        if self._db_settings:
            first_db_settings = next(iter(self._db_settings.values()))
            log_level_str = first_db_settings.get('LOG_LEVEL', 'INFO')
        
        log_level = getattr(logging, log_level_str)
        logger.setLevel(log_level)
        
        # Only add handler if none exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(name)s] %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
    def get_database_settings(self, db_alias):
        """Get settings for a specific database."""
        return self._db_settings.get(db_alias, {})
    
    def is_database_enabled(self, db_alias):
        """Check if universal constraints are enabled for this database."""
        return db_alias in self._db_settings
    
    def should_process_app(self, app_label, db_alias):
        """Determine if an app should be processed for a specific database."""
        if not self.is_database_enabled(db_alias):
            return False
        
        db_settings = self.get_database_settings(db_alias)
        
        # Simple exclude-based filtering
        exclude_apps = db_settings.get('EXCLUDE_APPS', [])
        return app_label not in exclude_apps
    
    def should_process_model(self, model, db_alias):
        """Determine if a specific model should be processed for a database."""
        return self.should_process_app(model._meta.app_label, db_alias)
    
    def get_setting(self, db_alias, setting_name, default=None):
        """Get a specific setting for a database."""
        db_settings = self.get_database_settings(db_alias)
        return db_settings.get(setting_name, default)
    
    def reload(self):
        """Reload settings from Django settings."""
        self._db_settings = {}
        self._load_settings()


# Global settings instance
constraint_settings = ConstraintSettings()
