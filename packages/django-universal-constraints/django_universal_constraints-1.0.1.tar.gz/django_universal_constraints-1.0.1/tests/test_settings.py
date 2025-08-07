"""
Tests for universal_constraints.settings module.
"""

import logging
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured

from universal_constraints.settings import ConstraintSettings, constraint_settings


class ConstraintSettingsTest(TestCase):
    """Test the ConstraintSettings class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.settings = ConstraintSettings()
    
    def test_default_settings(self):
        """Test default settings are applied correctly."""
        from universal_constraints.settings import DEFAULT_SETTINGS
        
        expected_defaults = {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
            'RACE_CONDITION_PROTECTION': True,
            'REMOVE_DB_CONSTRAINTS': True,
            'LOG_LEVEL': 'INFO',
        }
        
        self.assertEqual(DEFAULT_SETTINGS, expected_defaults)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'test_db': {
            'EXCLUDE_APPS': ['custom_app'],
            'LOG_LEVEL': 'DEBUG',
        }
    })
    def test_per_database_settings(self):
        """Test per-database settings configuration."""
        settings = ConstraintSettings()
        
        # Test database is enabled
        self.assertTrue(settings.is_database_enabled('test_db'))
        self.assertFalse(settings.is_database_enabled('other_db'))
        
        # Test settings are merged with defaults
        db_settings = settings.get_database_settings('test_db')
        self.assertEqual(db_settings['EXCLUDE_APPS'], ['custom_app'])  # Overridden
        self.assertEqual(db_settings['LOG_LEVEL'], 'DEBUG')  # Overridden
        self.assertTrue(db_settings['RACE_CONDITION_PROTECTION'])  # Default
        self.assertTrue(db_settings['REMOVE_DB_CONSTRAINTS'])  # Default
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'test_db': {
            'LOG_LEVEL': 'INVALID',
        }
    })
    def test_invalid_log_level(self):
        """Test validation of invalid log level."""
        with self.assertRaises(ValueError) as cm:
            ConstraintSettings()
        
        self.assertIn("Invalid LOG_LEVEL", str(cm.exception))
        self.assertIn("test_db", str(cm.exception))
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'test_db': {
            'RACE_CONDITION_PROTECTION': 'not_a_boolean',
        }
    })
    def test_invalid_boolean_setting(self):
        """Test validation of invalid boolean settings."""
        with self.assertRaises(ValueError) as cm:
            ConstraintSettings()
        
        self.assertIn("RACE_CONDITION_PROTECTION", str(cm.exception))
        self.assertIn("must be a boolean", str(cm.exception))
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'test_db': {
            'EXCLUDE_APPS': 'not_a_list',
        }
    })
    def test_invalid_exclude_apps(self):
        """Test validation of invalid EXCLUDE_APPS."""
        with self.assertRaises(ValueError) as cm:
            ConstraintSettings()
        
        self.assertIn("EXCLUDE_APPS", str(cm.exception))
        self.assertIn("must be a list", str(cm.exception))
    
    @override_settings(
        UNIVERSAL_CONSTRAINTS={
            'test_db': {
                'REMOVE_DB_CONSTRAINTS': True,
            }
        },
        DATABASES={
            'test_db': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
    )
    def test_backend_wrapper_warning(self):
        """Test warning when REMOVE_DB_CONSTRAINTS=True without wrapper."""
        with self.assertLogs('universal_constraints.settings', level='WARNING') as cm:
            ConstraintSettings()
        
        self.assertEqual(len(cm.output), 1)
        self.assertIn("REMOVE_DB_CONSTRAINTS=True", cm.output[0])
        self.assertIn("not using the universal_constraints backend wrapper", cm.output[0])
    
    @override_settings(
        UNIVERSAL_CONSTRAINTS={
            'test_db': {
                'REMOVE_DB_CONSTRAINTS': True,
            }
        },
        DATABASES={
            'test_db': {
                'ENGINE': 'universal_constraints.backend',
                'WRAPPED_ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
    )
    def test_no_warning_with_wrapper(self):
        """Test no warning when using wrapper with REMOVE_DB_CONSTRAINTS=True."""
        # When using the wrapper, no warnings should be logged
        # We can't use assertLogs because it expects logs to be present
        # Instead, we'll capture logs manually and verify none are generated
        import logging
        
        # Create a custom handler to capture logs
        log_messages = []
        handler = logging.Handler()
        handler.emit = lambda record: log_messages.append(record.getMessage())
        
        logger = logging.getLogger('universal_constraints.settings')
        original_level = logger.level
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        
        try:
            ConstraintSettings()
            # Check that no warning messages were logged
            warning_messages = [msg for msg in log_messages if 'REMOVE_DB_CONSTRAINTS=True' in msg]
            self.assertEqual(len(warning_messages), 0, "Expected no warnings but got: " + str(warning_messages))
        finally:
            logger.removeHandler(handler)
            logger.setLevel(original_level)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'test_db': {
            'EXCLUDE_APPS': ['admin', 'auth'],
        }
    })
    def test_should_process_app(self):
        """Test app processing logic."""
        settings = ConstraintSettings()
        
        # Should process apps not in exclude list
        self.assertTrue(settings.should_process_app('myapp', 'test_db'))
        self.assertTrue(settings.should_process_app('books', 'test_db'))
        
        # Should not process excluded apps
        self.assertFalse(settings.should_process_app('admin', 'test_db'))
        self.assertFalse(settings.should_process_app('auth', 'test_db'))
        
        # Should not process for disabled databases
        self.assertFalse(settings.should_process_app('myapp', 'other_db'))
    
    def test_get_setting(self):
        """Test getting specific settings."""
        with override_settings(UNIVERSAL_CONSTRAINTS={
            'test_db': {
                'RACE_CONDITION_PROTECTION': False,
            }
        }):
            settings = ConstraintSettings()
            
            # Test getting existing setting
            self.assertFalse(settings.get_setting('test_db', 'RACE_CONDITION_PROTECTION'))
            
            # Test getting setting with default
            self.assertEqual(
                settings.get_setting('test_db', 'NONEXISTENT', 'default_value'),
                'default_value'
            )
            
            # Test getting setting for non-existent database
            self.assertIsNone(settings.get_setting('other_db', 'RACE_CONDITION_PROTECTION'))
    
    def test_reload_settings(self):
        """Test reloading settings."""
        settings = ConstraintSettings()
        
        # Initially no databases enabled
        self.assertFalse(settings.is_database_enabled('test_db'))
        
        with override_settings(UNIVERSAL_CONSTRAINTS={
            'test_db': {'EXCLUDE_APPS': ['admin']}
        }):
            # Reload settings
            settings.reload()
            
            # Now database should be enabled
            self.assertTrue(settings.is_database_enabled('test_db'))
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        with override_settings(UNIVERSAL_CONSTRAINTS={
            'test_db': {'LOG_LEVEL': 'DEBUG'}
        }):
            settings = ConstraintSettings()
            
            # Check that logger level is set correctly
            logger = logging.getLogger('universal_constraints.settings')
            self.assertEqual(logger.level, logging.DEBUG)


class GlobalSettingsTest(TestCase):
    """Test the global constraint_settings instance."""
    
    def test_global_instance(self):
        """Test that global instance is properly initialized."""
        from universal_constraints.settings import constraint_settings
        
        self.assertIsInstance(constraint_settings, ConstraintSettings)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'test_db': {'EXCLUDE_APPS': ['admin']}
    })
    def test_global_instance_reflects_settings(self):
        """Test that global instance reflects Django settings."""
        # Reload to pick up test settings
        constraint_settings.reload()
        
        self.assertTrue(constraint_settings.is_database_enabled('test_db'))
