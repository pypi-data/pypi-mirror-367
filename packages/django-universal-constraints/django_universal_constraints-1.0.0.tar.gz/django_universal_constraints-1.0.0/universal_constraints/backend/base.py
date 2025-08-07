"""
Universal database wrapper backend for Django.

This module provides a database backend that can wrap any Django database backend
and add universal constraint support.
"""

import logging
import importlib
from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ImproperlyConfigured

from ..constraint_converter import ConstraintConverter
from ..validators import UniversalConstraint

logger = logging.getLogger('universal_constraints.backends')


class UniversalConstraintSchemaEditor:
    """
    Schema editor mixin that intercepts unique/conditional constraints.
    
    This mixin overrides key schema editor methods to:
    1. Detect unique/conditional constraints
    2. Convert them to application-level validation
    3. Filter them out from database creation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get database alias from connection
        self.db_alias = getattr(self.connection, 'alias', 'default')
        
        # Load database-specific settings
        self.db_settings = self._get_database_settings()
        
        # Only intercept if enabled for this database
        self.should_intercept = self.db_settings.get('REMOVE_DB_CONSTRAINTS', False)
        
        self.converter = ConstraintConverter(remove_db_constraints=self.should_intercept)
        self._intercepted_constraints = []
    
    def _get_database_settings(self):
        """Get settings specific to this database."""
        from universal_constraints.settings import constraint_settings
        return constraint_settings.get_database_settings(self.db_alias)
    
    def create_model(self, model):
        """
        Override create_model to intercept constraints during model creation.
        """
        logger.debug(f"Creating model {model._meta.label}")
        
        # Intercept and process constraints before creating the model
        self._intercept_model_constraints(model)
        
        # Call parent to create the model (with filtered constraints)
        super().create_model(model)
        
        # Register intercepted constraints for application-level validation
        self._register_intercepted_constraints(model)
    
    def add_constraint(self, model, constraint):
        """
        Override add_constraint to intercept individual constraint additions.
        """
        logger.debug(f"Adding constraint {constraint.name} to {model._meta.label}")
        
        # Convert to application-level constraint
        app_constraint = self._convert_constraint(constraint)
        
        # Register for application-level validation
        self._register_constraint(model, app_constraint)
    
    def remove_constraint(self, model, constraint):
        """
        Override remove_constraint to handle application-level constraints.
        """
        logger.debug(f"Removing constraint {constraint.name} from {model._meta.label}")
        
        # Check if this is an application-level constraint
        if hasattr(model, '_universal_constraints'):
            app_constraints = model._universal_constraints
            for i, app_constraint in enumerate(app_constraints):
                if app_constraint.name == constraint.name:
                    logger.info(f"Removing application-level constraint: {constraint.name}")
                    app_constraints.pop(i)
    
    def _intercept_model_constraints(self, model):
        """
        Intercept constraints during model creation.
        """
        original_constraints = list(model._meta.constraints)
        intercepted_constraints = []
        
        for constraint in original_constraints:
            logger.info(f"Intercepting constraint during model creation: {constraint.name}")
            intercepted_constraints.append(constraint)
        
        # Store intercepted constraints for later registration
        self._intercepted_constraints.extend([
            (model, constraint) for constraint in intercepted_constraints
        ])
    
    def _register_intercepted_constraints(self, model):
        """
        Register intercepted constraints for application-level validation.
        """
        model_constraints = [
            constraint for model_ref, constraint in self._intercepted_constraints
            if model_ref == model
        ]
        
        if model_constraints:
            logger.info(f"Registering {len(model_constraints)} intercepted constraints for {model._meta.label}")
            
            for constraint in model_constraints:
                app_constraint = self._convert_constraint(constraint)
                self._register_constraint(model, app_constraint)
    
    def _convert_constraint(self, constraint):
        """
        Convert a Django UniqueConstraint to a UniversalConstraint.
        """
        return UniversalConstraint(
            fields=constraint.fields,
            condition=getattr(constraint, 'condition', None),
            name=constraint.name
        )
    
    def _register_constraint(self, model, constraint):
        """
        Register a constraint for application-level validation.
        """
        if not hasattr(model, '_universal_constraints'):
            model._universal_constraints = []
        
        # Avoid duplicate registration
        existing_names = [c.name for c in model._universal_constraints]
        if constraint.name not in existing_names:
            model._universal_constraints.append(constraint)
            logger.debug(f"Registered constraint {constraint.name} for application-level validation")


class UniversalConstraintBackendMixin:
    """
    Mixin for Django database backends that adds conditional constraint support.
    
    This mixin can be used with any Django database backend to add automatic
    interception and conversion of unique/conditional constraints.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(f"Initialized conditional constraint backend wrapper")
    
    def _get_schema_editor_class(self, *args, **kwargs):
        """
        Return a schema editor class that includes constraint interception.
        """
        # Get the original schema editor class from the parent backend
        # Use the correct method name for Django database backends
        if hasattr(super(), '_get_schema_editor_class'):
            original_schema_editor_class = super()._get_schema_editor_class(*args, **kwargs)
        else:
            # Fallback for backends that don't have this method
            from django.db.backends.base.schema import BaseDatabaseSchemaEditor
            original_schema_editor_class = BaseDatabaseSchemaEditor
        
        # Create a new class that combines our mixin with the original
        class WrappedSchemaEditor(UniversalConstraintSchemaEditor, original_schema_editor_class):
            pass
        
        return WrappedSchemaEditor
    
    def get_new_connection(self, conn_params):
        """
        Override to ensure our schema editor is used.
        """
        connection = super().get_new_connection(conn_params)
        logger.debug("Created new database connection with constraint interception")
        return connection


class DatabaseWrapper(UniversalConstraintBackendMixin):
    """
    Universal database wrapper that works with any Django database backend.
    
    This wrapper dynamically inherits from the specified backend and adds
    unique/conditional constraint interception capabilities.
    
    Usage in settings.py:
        DATABASES = {
            'default': {
                'ENGINE': 'universal_constraints.backend',
                'WRAPPED_ENGINE': 'django.db.backends.sqlite3',  # Any Django backend
                'NAME': 'db.sqlite3',
                # ... other settings
            }
        }
    """
    
    def __init__(self, settings_dict, alias=None):
        # Get the backend to wrap
        wrapped_engine = settings_dict.get('WRAPPED_ENGINE')
        if not wrapped_engine:
            raise ImproperlyConfigured(
                "WRAPPED_ENGINE must be specified when using "
                "universal_constraints.backend"
            )
        
        logger.info(f"Wrapping database backend: {wrapped_engine}")
        
        try:
            # Import the wrapped backend module
            backend_module = importlib.import_module(f'{wrapped_engine}.base')
            wrapped_backend_class = backend_module.DatabaseWrapper
            
            logger.debug(f"Successfully imported backend: {wrapped_backend_class}")
            
        except ImportError as e:
            # Provide more helpful error messages for common issues
            error_msg = f"Could not import database backend '{wrapped_engine}': {e}"
            
            if 'No module named' in str(e):
                error_msg += (
                    f"\n\nTroubleshooting tips:\n"
                    f"1. Ensure '{wrapped_engine}' is installed: pip install <package-name>\n"
                    f"2. Check that the engine path is correct (e.g., 'django.db.backends.sqlite3')\n"
                    f"3. Verify the package is in your Python path\n"
                    f"4. For third-party backends, ensure they're properly installed and configured"
                )
            
            raise ImproperlyConfigured(error_msg)
        except AttributeError as e:
            raise ImproperlyConfigured(
                f"Backend '{wrapped_engine}' does not have a DatabaseWrapper class: {e}\n"
                f"This may not be a valid Django database backend."
            )
        
        # Dynamically create a new class that inherits from both our mixin
        # and the wrapped backend
        wrapper_class = type(
            'DatabaseWrapper',
            (UniversalConstraintBackendMixin, wrapped_backend_class),
            {
                '__module__': __name__,
                'wrapped_engine': wrapped_engine,
                'display_name': property(lambda self: f"Conditional Constraint Wrapper ({getattr(self, 'wrapped_engine', 'unknown')})"),
                '__repr__': lambda self: f"<DatabaseWrapper: {getattr(self, 'wrapped_engine', 'unknown')} with universal constraint support>",
            }
        )
        
        # Replace our class with the new hybrid class
        self.__class__ = wrapper_class
        
        logger.debug(f"Created hybrid wrapper class: {wrapper_class.__mro__}")
        
        # Initialize with the wrapped backend's initialization
        # Use the wrapper class directly since we changed self.__class__
        wrapper_class.__init__(self, settings_dict, alias)
        
        logger.info(f"Successfully initialized wrapped backend for {alias or 'default'}")
    
    @property
    def display_name(self):
        """Return a display name that shows both the wrapper and wrapped backend."""
        wrapped_engine = getattr(self, 'wrapped_engine', 'unknown')
        return f"Conditional Constraint Wrapper ({wrapped_engine})"
    
    def __repr__(self):
        wrapped_engine = getattr(self, 'wrapped_engine', 'unknown')
        return f"<DatabaseWrapper: {wrapped_engine} with universal constraint support>"
