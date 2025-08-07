"""
Shared utilities for constraint discovery and management.

This module contains common functions used by both auto_discovery.py
and the discover_constraints management command to eliminate code duplication.
"""

import logging
from django.apps import apps
from django.conf import settings as django_settings

from .constraint_converter import has_universal_constraints

logger = logging.getLogger('universal_constraints.utils')


def should_process_model_for_database(model, db_alias):
    """
    Check if a model should be processed for a specific database based on database routing.
    
    Args:
        model: Django model class
        db_alias: Database alias
        
    Returns:
        bool: True if model should be processed for this database
    """
    from django.db import router
    
    # Use Django's database routing to determine if this model belongs to this database
    # Check both read and write routing to be comprehensive
    read_db = router.db_for_read(model)
    write_db = router.db_for_write(model)
    
    # If routing returns None, it means the model can use any database
    # In that case, we'll process it for the 'default' database only to avoid duplicates
    if read_db is None and write_db is None:
        return db_alias == 'default'
    
    # If either read or write routing points to this database, process it
    return read_db == db_alias or write_db == db_alias


def get_database_constraint_status(db_alias, db_settings):
    """
    Get constraint handling status for a database.
    
    Args:
        db_alias: Database alias
        db_settings: Database settings from constraint_settings
        
    Returns:
        str: Description of constraint handling status
    """
    remove_db_constraints = db_settings.get('REMOVE_DB_CONSTRAINTS', False)
    
    # Check if using backend wrapper
    db_config = django_settings.DATABASES.get(db_alias, {})
    engine = db_config.get('ENGINE', '')
    using_wrapper = 'universal_constraints.backend' in engine
    
    # Determine constraint handling
    if remove_db_constraints and using_wrapper:
        return "constraints removed from DB schema"
    elif remove_db_constraints and not using_wrapper:
        return "constraints kept in DB schema (no wrapper)"
    else:
        return "constraints kept in DB schema"


def collect_models_for_database(db_alias, constraint_settings):
    """
    Collect models that should be processed for a specific database.
    
    Args:
        db_alias: Database alias
        constraint_settings: Constraint settings instance
        
    Returns:
        list: Models that should be processed for this database
    """
    models_to_process = []
    
    # Process based on app filtering and database routing for this database
    for model in apps.get_models():
        if (has_universal_constraints(model) and 
            constraint_settings.should_process_app(model._meta.app_label, db_alias) and
            should_process_model_for_database(model, db_alias)):
            models_to_process.append(model)
    
    return models_to_process


def should_process_model(model, db_alias, constraint_settings):
    """
    Check if a model should be processed based on both app filtering and database routing.
    
    Args:
        model: Django model class
        db_alias: Database alias
        constraint_settings: Constraint settings instance
        
    Returns:
        bool: True if model should be processed
    """
    # First check constraint settings (includes app filtering)
    if not constraint_settings.should_process_model(model, db_alias):
        return False
    
    # Then check database routing
    return should_process_model_for_database(model, db_alias)
