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
from .constraint_converter import ConstraintConverter, has_convertible_constraints

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
            self.converters[db_alias] = ConstraintConverter()
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
    
    def _get_models_to_process(self, db_alias):
        """Get list of models to process for a specific database."""
        from django.db import router
        
        models_to_process = []
        
        # Process based on app filtering and database routing for this database
        for model in apps.get_models():
            if not has_convertible_constraints(model):
                continue
                
            if not self.settings.should_process_app(model._meta.app_label, db_alias):
                continue
                
            # Use Django's database routing to determine if this model belongs to this database
            read_db = router.db_for_read(model)
            write_db = router.db_for_write(model)
            
            # If routing returns None, it means the model can use any database
            # In that case, we'll process it for the 'default' database only to avoid duplicates
            if read_db is None and write_db is None:
                if db_alias == 'default':
                    models_to_process.append(model)
            # If either read or write routing points to this database, process it
            elif read_db == db_alias or write_db == db_alias:
                models_to_process.append(model)
        
        return models_to_process
    
    
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


def auto_discover_constraints():
    """
    Run auto-discovery with current settings.
    
    Returns:
        dict: Summary of discovery results
    """
    discovery = AutoDiscovery()
    return discovery.discover_all()


def discover_model_constraints(model, db_alias='default'):
    """
    Discover constraints for a specific model.
    
    Args:
        model: Django model class or model string ('app.Model')
        db_alias: Database alias to use for settings
    
    Returns:
        list: Converted constraints
    """
    if isinstance(model, str):
        app_label, model_name = model.split('.')
        model = apps.get_model(app_label, model_name)
    
    discovery = AutoDiscovery()
    return discovery.discover_model(model, db_alias)
