from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger('universal_constraints.apps')


class UniqueConstraintsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'universal_constraints'
    
    def ready(self):
        """Initialize the unique constraints system when the app is ready."""
        # Import signal handlers to ensure they're registered
        from . import validators
        
        # Run auto-discovery for configured databases
        self._run_auto_discovery()
    
    def _run_auto_discovery(self):
        """Run auto-discovery for all configured databases."""
        try:
            from .auto_discovery import auto_discover_constraints
            from .settings import constraint_settings
            
            # Get all configured databases
            configured_databases = list(constraint_settings._db_settings.keys())
            
            if configured_databases:
                logger.info(f"Running auto-discovery for databases: {', '.join(configured_databases)}")
                summary = auto_discover_constraints()
                
                if summary['constraints_converted'] > 0:
                    logger.info(
                        f"Auto-discovery completed: {summary['constraints_converted']} "
                        f"constraints converted from {summary['models_processed']} models"
                    )
                else:
                    logger.info("Auto-discovery completed: no constraints found to convert")
            else:
                logger.debug("No databases configured for universal constraints")
                
        except Exception as e:
            logger.error(f"Error during auto-discovery: {e}")
            # Don't raise the exception to avoid breaking Django startup
