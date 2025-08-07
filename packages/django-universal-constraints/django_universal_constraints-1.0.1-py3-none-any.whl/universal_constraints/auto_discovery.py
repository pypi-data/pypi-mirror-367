"""
Auto-discovery system for constraints.

This module automatically discovers and converts Django's native unique constraints
to application-level validation for backends that don't support them natively.
"""

import logging
from django.apps import apps
from django.db import models
from django.conf import settings as django_settings

from .settings import constraint_settings
from .constraint_converter import ConstraintConverter, has_universal_constraints
from .utils import should_process_model_for_database, get_database_constraint_status, collect_models_for_database

logger = logging.getLogger('universal_constraints.discovery')


class AutoDiscovery:
    """Automatically discovers and converts unique constraints across Django models."""
    
    def __init__(self, settings=None):
        self.settings = settings or constraint_settings
        self.processed_models = set()
        self.total_converted = 0
        self.converters = {}  # Per-database converters
    
    def discover_all(self):
        """
        Discover and convert constraints for all models based on per-database configuration.
        
        Returns:
            dict: Summary of discovery results
        """
        logger.info("Starting auto-discovery of unique constraints")
        
        # Get enabled databases
        enabled_databases = self._get_enabled_databases()
        
        if not enabled_databases:
            logger.info("Auto-discovery disabled for all databases")
            return self._get_summary()
        
        logger.info(f"Auto-discovery enabled for databases: {', '.join(enabled_databases)}")
        
        # Process models for each enabled database
        total_models_processed = 0
        
        for db_alias in enabled_databases:
            models_to_process = self._get_models_to_process(db_alias)
            
            if not models_to_process:
                logger.debug(f"No models found to process for database '{db_alias}'")
                continue
            
            logger.info(f"Found {len(models_to_process)} model(s) to process for database '{db_alias}'")
            
            # Get or create converter for this database
            converter = self._get_converter_for_database(db_alias)
            
            # Process each model
            for model in models_to_process:
                try:
                    self._process_model(model, db_alias, converter)
                    total_models_processed += 1
                except Exception as e:
                    model_label = getattr(model, '_meta', {}).get('label', str(model))
                    logger.error(
                        f"Error processing model {model_label} for database '{db_alias}': {e}. "
                        f"Skipping this model and continuing with others."
                    )
                    # Add to warnings for summary
                    converter.warnings.append(f"Failed to process model {model_label}: {e}")
        
        # Log summary
        total_converted = sum(converter.get_stats()['converted'] for converter in self.converters.values())
        total_warnings = sum(len(converter.get_warnings()) for converter in self.converters.values())
        
        logger.info(
            f"Auto-discovery complete: {total_converted} constraints converted, "
            f"{total_warnings} warnings across {len(enabled_databases)} database(s)"
        )
        
        # Log warnings from all converters
        for db_alias, converter in self.converters.items():
            for warning in converter.get_warnings():
                logger.warning(f"[{db_alias}] {warning}")
        
        return self._get_summary()
    
    def _get_enabled_databases(self):
        """Get list of databases with universal constraints configured."""
        universal_constraints_config = getattr(django_settings, 'UNIVERSAL_CONSTRAINTS', {})
        return list(universal_constraints_config.keys())
    
    def _get_converter_for_database(self, db_alias):
        """Get or create a converter for a specific database."""
        if db_alias not in self.converters:
            db_settings = self.settings.get_database_settings(db_alias)
            
            # Only remove DB constraints if using our backend wrapper
            remove_db_constraints = False
            if db_settings.get('REMOVE_DB_CONSTRAINTS', False):
                db_config = django_settings.DATABASES.get(db_alias, {})
                engine = db_config.get('ENGINE', '')
                if 'universal_constraints.backend' in engine:
                    remove_db_constraints = True
                    logger.debug(f"Database '{db_alias}' using backend wrapper - will remove DB constraints")
                else:
                    logger.debug(f"Database '{db_alias}' not using backend wrapper - will keep DB constraints")
            
            self.converters[db_alias] = ConstraintConverter(
                remove_db_constraints=remove_db_constraints
            )
        return self.converters[db_alias]
    
    def discover_model(self, model, db_alias='default'):
        """
        Discover and convert constraints for a specific model.
        
        Args:
            model: Django model class
            db_alias: Database alias to use for settings
        
        Returns:
            list: Converted constraints for the model
        """
        logger.debug(f"Processing specific model: {model._meta.label} for database '{db_alias}'")
        converter = self._get_converter_for_database(db_alias)
        return self._process_model(model, db_alias, converter)
    
    def discover_app(self, app_label, db_alias='default'):
        """
        Discover and convert constraints for all models in a specific app.
        
        Args:
            app_label: Django app label
            db_alias: Database alias to use for settings
        
        Returns:
            dict: Summary of results for the app
        """
        logger.info(f"Processing app: {app_label} for database '{db_alias}'")
        
        try:
            app_models = apps.get_app_config(app_label).get_models()
        except LookupError:
            logger.error(f"App '{app_label}' not found")
            return {'error': f"App '{app_label}' not found"}
        
        processed = 0
        converted_constraints = []
        converter = self._get_converter_for_database(db_alias)
        
        for model in app_models:
            if has_universal_constraints(model) and self.settings.should_process_app(model._meta.app_label, db_alias):
                constraints = self._process_model(model, db_alias, converter)
                converted_constraints.extend(constraints)
                processed += 1
        
        logger.info(f"Processed {processed} model(s) in app '{app_label}' for database '{db_alias}'")
        
        return {
            'app': app_label,
            'database': db_alias,
            'models_processed': processed,
            'constraints_converted': len(converted_constraints),
            'constraints': converted_constraints
        }
    
    def _get_models_to_process(self, db_alias):
        """Get list of models to process for a specific database."""
        return collect_models_for_database(db_alias, self.settings)
    
    
    def _process_model(self, model, db_alias, converter):
        """Process a single model for constraint conversion."""
        model_key = (model, db_alias)
        if model_key in self.processed_models:
            logger.debug(f"Model {model._meta.label} already processed for database '{db_alias}', skipping")
            return []
        
        logger.debug(f"Processing model: {model._meta.label} for database '{db_alias}'")
        
        # Convert constraints
        converted_constraints = converter.convert_model_constraints(model)
        
        # Mark as processed
        self.processed_models.add(model_key)
        
        if converted_constraints:
            logger.info(
                f"Converted {len(converted_constraints)} constraint(s) for {model._meta.label} (database: {db_alias})"
            )
        else:
            logger.debug(f"No constraints converted for {model._meta.label} (database: {db_alias})")
        
        return converted_constraints
    
    def _get_summary(self):
        """Get summary of discovery results."""
        if not self.converters:
            return {
                'enabled': False,
                'models_processed': 0,
                'constraints_converted': 0,
                'constraints_skipped': 0,
                'warnings': 0,
                'warning_messages': [],
                'databases': {}
            }
        
        # Aggregate stats from all converters
        total_converted = sum(converter.get_stats()['converted'] for converter in self.converters.values())
        total_skipped = sum(converter.get_stats()['skipped'] for converter in self.converters.values())
        total_warnings = sum(converter.get_stats()['warnings'] for converter in self.converters.values())
        all_warning_messages = []
        
        database_stats = {}
        for db_alias, converter in self.converters.items():
            stats = converter.get_stats()
            db_settings = self.settings.get_database_settings(db_alias)
            database_stats[db_alias] = {
                'constraints_converted': stats['converted'],
                'constraints_skipped': stats['skipped'],
                'warnings': stats['warnings'],
                'warning_messages': converter.get_warnings(),
                'settings': {
                    'race_protection': db_settings.get('RACE_CONDITION_PROTECTION', True),
                    'remove_db_constraints': db_settings.get('REMOVE_DB_CONSTRAINTS', True),
                    'exclude_apps': db_settings.get('EXCLUDE_APPS', []),
                }
            }
            all_warning_messages.extend(converter.get_warnings())
        
        return {
            'enabled': len(self.converters) > 0,
            'models_processed': len(self.processed_models),
            'constraints_converted': total_converted,
            'constraints_skipped': total_skipped,
            'warnings': total_warnings,
            'warning_messages': all_warning_messages,
            'databases': database_stats
        }


# Global discovery instance
_discovery_instance = None


def get_discovery_instance():
    """Get or create the global discovery instance."""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = AutoDiscovery()
    return _discovery_instance


def auto_discover_constraints():
    """
    Convenience function to run auto-discovery with current settings.
    
    Returns:
        dict: Summary of discovery results
    """
    discovery = get_discovery_instance()
    return discovery.discover_all()


def discover_model_constraints(model, db_alias='default'):
    """
    Convenience function to discover constraints for a specific model.
    
    Args:
        model: Django model class or model string ('app.Model')
        db_alias: Database alias to use for settings
    
    Returns:
        list: Converted constraints
    """
    if isinstance(model, str):
        app_label, model_name = model.split('.')
        model = apps.get_model(app_label, model_name)
    
    discovery = get_discovery_instance()
    return discovery.discover_model(model, db_alias)


def discover_app_constraints(app_label):
    """
    Convenience function to discover constraints for all models in an app.
    
    Args:
        app_label: Django app label
    
    Returns:
        dict: Summary of results for the app
    """
    discovery = get_discovery_instance()
    return discovery.discover_app(app_label)


def get_discovery_summary():
    """
    Get summary of the last discovery run.
    
    Returns:
        dict: Summary information
    """
    discovery = get_discovery_instance()
    return discovery._get_summary()


def reset_discovery():
    """Reset the global discovery instance (useful for testing)."""
    global _discovery_instance
    _discovery_instance = None
